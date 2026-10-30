import os
import shutil
import sqlite3
import tarfile
import tempfile
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import connections


class Command(BaseCommand):
    help = (
        "Create or restore a WAL-safe online SQLite database + media archive (.tar.gz) "
        "with automatic backup retention pruning."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--output-dir",
            type=str,
            default=os.getenv(
                "DJANGO_BACKUP_DIR",
                str(Path(settings.BASE_DIR) / "backups"),
            ),
            help="Directory to write backup .tar.gz archives (default: /app/backups).",
        )
        parser.add_argument(
            "--keep",
            type=int,
            default=int(os.getenv("DJANGO_BACKUP_RETENTION_COUNT", "7")),
            help="Number of recent backup archives to keep (0 = unlimited).",
        )
        parser.add_argument(
            "--db-path",
            type=str,
            default="",
            help="Optional explicit path to the SQLite database file.",
        )
        parser.add_argument(
            "--restore",
            type=str,
            default="",
            help=(
                "Path to a backup .tar.gz archive to restore into "
                "SQLite and MEDIA_ROOT."
            ),
        )

    def handle(self, *args: Any, **options: Any) -> str:
        explicit_db = (options.get("db_path") or "").strip()
        restore_path = (options.get("restore") or "").strip()
        if restore_path:
            return self._restore_backup(Path(restore_path), explicit_db=explicit_db)

        output_dir = Path(options["output_dir"])
        keep = int(options["keep"])
        return self._create_backup(
            output_dir=output_dir,
            keep=keep,
            explicit_db=explicit_db,
        )

    def _resolve_sqlite_path(self, explicit_db: str = "") -> Path:
        db_name = explicit_db or str(settings.DATABASES["default"]["NAME"])
        if db_name == ":memory:" or "mode=memory" in db_name:
            msg = "Cannot run file backup against an in-memory SQLite database."
            raise CommandError(msg)
        return Path(db_name)

    def _create_backup(
        self,
        *,
        output_dir: Path,
        keep: int,
        explicit_db: str = "",
    ) -> str:
        sqlite_path = self._resolve_sqlite_path(explicit_db)
        if not sqlite_path.exists():
            # Ensure connection is initialized so the SQLite file exists on disk
            connections["default"].ensure_connection()

        if not sqlite_path.exists():
            msg = f"SQLite database file not found at {sqlite_path}"
            raise CommandError(msg)

        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S-%f")
        archive_path = output_dir / f"web-result-backup-{timestamp}.tar.gz"

        media_root = Path(settings.MEDIA_ROOT)

        with tempfile.TemporaryDirectory() as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            snapshot_db = tmp_dir / "db.sqlite3"

            # Perform an atomic online SQLite backup (WAL-safe even during live writes)
            src_conn = sqlite3.connect(str(sqlite_path), timeout=30)
            dst_conn = sqlite3.connect(str(snapshot_db))
            try:
                with dst_conn:
                    src_conn.backup(dst_conn)
            finally:
                dst_conn.close()
                src_conn.close()

            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(snapshot_db, arcname="db.sqlite3")
                if media_root.exists():
                    tar.add(media_root, arcname="media")

        # Also keep a copy inside DATA_DIR/backups/latest.tar.gz so a Coolify volume
        # backup of `sqlite-data` (/app/data) always captures a WAL-consistent archive
        data_dir = Path(getattr(settings, "DATA_DIR", sqlite_path.parent))
        data_backups_dir = data_dir / "backups"
        try:
            data_backups_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(archive_path, data_backups_dir / "latest.tar.gz")
        except OSError:
            pass

        pruned = self._prune_old_backups(output_dir=output_dir, keep=keep)
        self.stdout.write(
            self.style.SUCCESS(
                f"Created backup archive: {archive_path} "
                f"(pruned {pruned} old archive(s))",
            ),
        )
        return str(archive_path)

    def _prune_old_backups(self, *, output_dir: Path, keep: int) -> int:
        if keep <= 0:
            return 0
        archives = sorted(
            output_dir.glob("web-result-backup-*.tar.gz"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        pruned = 0
        for old_archive in archives[keep:]:
            old_archive.unlink(missing_ok=True)
            pruned += 1
        return pruned

    def _restore_backup(self, archive_path: Path, explicit_db: str = "") -> str:
        if not archive_path.exists():
            msg = f"Backup archive not found: {archive_path}"
            raise CommandError(msg)

        sqlite_path = self._resolve_sqlite_path(explicit_db)
        media_root = Path(settings.MEDIA_ROOT)

        default_db_name = str(settings.DATABASES["default"]["NAME"])
        if not explicit_db and "memory" not in default_db_name:
            connections["default"].close()

        with tempfile.TemporaryDirectory() as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            with tarfile.open(archive_path, "r:gz") as tar:
                for member in tar.getmembers():
                    member_path = (tmp_dir / member.name).resolve()
                    if not str(member_path).startswith(str(tmp_dir.resolve())):
                        msg = f"Unsafe path in backup archive: {member.name}"
                        raise CommandError(msg)
                tar.extractall(path=tmp_dir, filter="data")

            extracted_db = tmp_dir / "db.sqlite3"
            if not extracted_db.exists():
                msg = "Archive does not contain db.sqlite3"
                raise CommandError(msg)

            sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            src_conn = sqlite3.connect(str(extracted_db))
            dst_conn = sqlite3.connect(str(sqlite_path), timeout=30)
            try:
                with dst_conn:
                    src_conn.backup(dst_conn)
            finally:
                dst_conn.close()
                src_conn.close()

            extracted_media = tmp_dir / "media"
            if extracted_media.exists():
                media_root.mkdir(parents=True, exist_ok=True)
                for src_file in extracted_media.rglob("*"):
                    if not src_file.is_file():
                        continue
                    rel = src_file.relative_to(extracted_media)
                    dest = media_root / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dest)

        self.stdout.write(
            self.style.SUCCESS(
                f"Restored SQLite database and media from {archive_path}",
            ),
        )
        return str(archive_path)
