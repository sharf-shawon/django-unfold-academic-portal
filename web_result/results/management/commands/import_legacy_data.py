import os
import re
import shutil
from datetime import date
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import unquote
from urllib.parse import urlparse

import pymysql
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.core.management.color import no_style
from django.db import connection
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.dateparse import parse_datetime

from web_result.results.models import Course
from web_result.results.models import Result
from web_result.results.models import Semester
from web_result.results.models import Student
from web_result.results.models import StudentCourse

User = get_user_model()

DEFAULT_COLUMNS: dict[str, list[str]] = {
    "semesters": ["id", "name", "year", "created_at", "updated_at"],
    "courses": ["id", "name", "code", "semester_id", "created_at", "updated_at"],
    "students": [
        "id",
        "student_id",
        "name",
        "email",
        "phone",
        "address",
        "session",
        "department",
        "date_of_birth",
        "date_of_issue",
        "cgpa",
        "image",
        "created_at",
        "updated_at",
    ],
    "course_student": ["course_id", "student_id"],
    "results": ["id", "course_id", "student_id", "gpa", "created_at", "updated_at"],
}

INSERT_REGEX = re.compile(
    r"INSERT\s+INTO\s+`?(?P<table>\w+)`?\s*"
    r"(?:\((?P<columns>[^)]+)\))?\s*"
    r"VALUES\s*(?P<values>.+?);",
    re.IGNORECASE | re.DOTALL,
)

ESCAPE_MAP = {"n": "\n", "r": "\r", "t": "\t"}


def _finalize_token(chars: list[str], *, is_string: bool) -> Any:
    raw = "".join(chars)
    if is_string:
        return raw
    stripped = raw.strip()
    if stripped.upper() == "NULL" or stripped == "":
        return None
    return stripped


def parse_sql_tuples(values_str: str) -> list[list[Any]]:  # noqa: C901, PLR0912
    """Parse a SQL VALUES clause `(...), (...)` into Python lists of values."""
    rows: list[list[Any]] = []
    current_row: list[Any] = []
    current_token: list[str] = []
    in_row = False
    in_string = False
    string_visited = False
    escape = False

    for ch in values_str:
        if not in_row:
            if ch == "(":
                in_row = True
                current_row = []
                current_token = []
                string_visited = False
            continue

        if in_string:
            if escape:
                current_token.append(ESCAPE_MAP.get(ch, ch))
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "'":
                in_string = False
            else:
                current_token.append(ch)
        elif ch == "'":
            if not string_visited:
                current_token = []
            else:
                current_token.append("'")
            in_string = True
            string_visited = True
        elif ch == ",":
            current_row.append(_finalize_token(current_token, is_string=string_visited))
            current_token = []
            string_visited = False
        elif ch == ")":
            current_row.append(_finalize_token(current_token, is_string=string_visited))
            rows.append(current_row)
            in_row = False
        else:
            current_token.append(ch)

    return rows


def parse_mysql_dump(sql_text: str) -> dict[str, list[dict[str, Any]]]:
    """Extract rows for supported legacy tables from a MySQL dump string."""
    tables: dict[str, list[dict[str, Any]]] = {k: [] for k in DEFAULT_COLUMNS}
    for match in INSERT_REGEX.finditer(sql_text):
        table_name = match.group("table").lower()
        if table_name not in tables:
            continue
        cols_group = match.group("columns")
        if cols_group:
            columns = [c.strip().strip("`\"'") for c in cols_group.split(",")]
        else:
            columns = DEFAULT_COLUMNS[table_name]
        tuples = parse_sql_tuples(match.group("values"))
        for row_values in tuples:
            row_dict = dict(zip(columns, row_values, strict=False))
            tables[table_name].append(row_dict)
    return tables


def fetch_mysql_tables(mysql_url: str) -> dict[str, list[dict[str, Any]]]:
    """Fetch rows directly from a live MySQL database URL."""
    parsed = urlparse(mysql_url)
    connection_params = {
        "host": parsed.hostname or "127.0.0.1",
        "port": parsed.port or 3306,
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
        "database": (parsed.path or "").lstrip("/"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
    }
    tables: dict[str, list[dict[str, Any]]] = {k: [] for k in DEFAULT_COLUMNS}
    conn = pymysql.connect(**connection_params)
    try:
        with conn.cursor() as cursor:
            for table_name in DEFAULT_COLUMNS:
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                if cursor.fetchone():
                    cursor.execute(f"SELECT * FROM `{table_name}`")  # noqa: S608
                    tables[table_name] = list(cursor.fetchall())
    finally:
        conn.close()
    return tables


def _coerce_date(value: Any) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    parsed = parse_date(str(value).strip())
    if parsed is None:
        msg = f"Invalid date value: {value!r}"
        raise ValueError(msg)
    return parsed


def _coerce_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    dt = value if isinstance(value, datetime) else parse_datetime(str(value).strip())
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def _normalize_image_path(value: Any) -> str | None:
    if not value:
        return None
    cleaned = str(value).strip().lstrip("/")
    if cleaned.startswith("uploads/"):
        cleaned = cleaned[len("uploads/") :]
    if "/" not in cleaned:
        cleaned = f"images/{cleaned}"
    return cleaned


class Command(BaseCommand):
    help = (
        "Import legacy MySQL academic records (semesters, courses, students, "
        "course_student, results), migrate uploaded student images, and optionally "
        "seed the demo admin account."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--sql-file",
            type=str,
            help="Path to a MySQL .sql dump file containing INSERT statements.",
        )
        parser.add_argument(
            "--mysql-url",
            type=str,
            default=os.getenv("LEGACY_MYSQL_URL", ""),
            help="MySQL connection URL (mysql://user:pass@host:port/dbname).",
        )
        parser.add_argument(
            "--uploads-dir",
            type=str,
            default="",
            help=(
                "Directory containing legacy uploaded files "
                "(e.g., ./old/public/uploads)."
            ),
        )
        parser.add_argument(
            "--seed-demo-user",
            action="store_true",
            help="Create or update the demo admin user (demo@shawon.me / demo1234).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        sql_file: str | None = options.get("sql_file")
        mysql_url: str = options.get("mysql_url") or ""
        uploads_dir = self._resolve_uploads_dir(options.get("uploads_dir") or "")
        seed_demo_user: bool = bool(options.get("seed_demo_user"))

        if not any([sql_file, mysql_url, uploads_dir, seed_demo_user]):
            msg = (
                "Provide at least one action: --sql-file, --mysql-url, "
                "--uploads-dir, or --seed-demo-user."
            )
            raise CommandError(msg)

        if seed_demo_user:
            self._seed_demo_account()

        tables = self._load_tables(sql_file=sql_file, mysql_url=mysql_url)
        if tables is not None:
            self._import_tables(tables)

        if uploads_dir:
            self._migrate_uploads(Path(uploads_dir))

    def _resolve_uploads_dir(self, explicit_dir: str) -> str:
        if explicit_dir:
            return explicit_dir
        default_uploads = Path(settings.BASE_DIR) / "old" / "public" / "uploads"
        return str(default_uploads) if default_uploads.exists() else ""

    def _load_tables(
        self,
        *,
        sql_file: str | None,
        mysql_url: str,
    ) -> dict[str, list[dict[str, Any]]] | None:
        if sql_file:
            sql_path = Path(sql_file)
            if not sql_path.exists():
                msg = f"SQL file not found: {sql_path}"
                raise CommandError(msg)
            return parse_mysql_dump(sql_path.read_text(encoding="utf-8"))
        if mysql_url:
            return fetch_mysql_tables(mysql_url)
        return None

    def _seed_demo_account(self) -> None:
        accounts = [("demo@shawon.me", "demo1234", "Demo")]
        custom_email = os.getenv("DJANGO_ADMIN_EMAIL", "").strip()
        custom_password = os.getenv("DJANGO_ADMIN_PASSWORD", "").strip()
        if (
            custom_email
            and custom_password
            and not custom_email.startswith("$")
            and not custom_password.startswith("$")
            and (custom_email, custom_password) != ("demo@shawon.me", "demo1234")
        ):
            accounts.append((custom_email, custom_password, "Admin"))

        for email, password, name in accounts:
            user, created = User.objects.update_or_create(
                email=email,
                defaults={
                    "name": name,
                    "is_staff": True,
                    "is_superuser": True,
                    "is_active": True,
                },
            )
            user.set_password(password)
            user.save()
            EmailAddress.objects.update_or_create(
                user=user,
                email=email,
                defaults={"verified": True, "primary": True},
            )
            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} demo admin user: {email}",
                ),
            )

    def _import_tables(self, tables: dict[str, list[dict[str, Any]]]) -> None:
        counts = dict.fromkeys(DEFAULT_COLUMNS, 0)
        with transaction.atomic():
            for row in tables.get("semesters", []):
                semester_id = int(row["id"])
                obj, _ = Semester.objects.update_or_create(
                    id=semester_id,
                    defaults={
                        "name": str(row["name"]),
                        "year": str(row["year"]),
                    },
                )
                self._apply_timestamps(Semester, obj.pk, row)
                counts["semesters"] += 1

            for row in tables.get("courses", []):
                course_id = int(row["id"])
                obj, _ = Course.objects.update_or_create(
                    id=course_id,
                    defaults={
                        "name": str(row["name"]),
                        "code": str(row["code"]),
                        "semester_id": int(row["semester_id"]),
                    },
                )
                self._apply_timestamps(Course, obj.pk, row)
                counts["courses"] += 1

            for row in tables.get("students", []):
                pk = int(row["id"])
                obj, _ = Student.objects.update_or_create(
                    id=pk,
                    defaults={
                        "student_id": str(row["student_id"]),
                        "name": str(row["name"]),
                        "email": str(row["email"]),
                        "phone": str(row["phone"]),
                        "address": str(row["address"]),
                        "session": str(row["session"]),
                        "department": str(row["department"]),
                        "date_of_birth": _coerce_date(row["date_of_birth"]),
                        "date_of_issue": _coerce_date(row["date_of_issue"]),
                        "cgpa": Decimal(str(row.get("cgpa") or "0.00")),
                        "image": _normalize_image_path(row.get("image")),
                    },
                )
                self._apply_timestamps(Student, obj.pk, row)
                counts["students"] += 1

            for row in tables.get("course_student", []):
                StudentCourse.objects.get_or_create(
                    course_id=int(row["course_id"]),
                    student_id=int(row["student_id"]),
                )
                counts["course_student"] += 1

            for row in tables.get("results", []):
                result_id = int(row["id"])
                obj, _ = Result.objects.update_or_create(
                    id=result_id,
                    defaults={
                        "course_id": int(row["course_id"]),
                        "student_id": int(row["student_id"]),
                        "gpa": Decimal(str(row["gpa"])),
                    },
                )
                self._apply_timestamps(Result, obj.pk, row)
                counts["results"] += 1

            self._reset_sequences([Semester, Course, Student, StudentCourse, Result])

        self.stdout.write(
            self.style.SUCCESS(
                "Imported legacy records: "
                f"semesters={counts['semesters']}, "
                f"courses={counts['courses']}, "
                f"students={counts['students']}, "
                f"course_student={counts['course_student']}, "
                f"results={counts['results']}",
            ),
        )

    def _apply_timestamps(self, model_cls, pk: int, row: dict[str, Any]) -> None:
        updates: dict[str, Any] = {}
        created_at = _coerce_datetime(row.get("created_at"))
        updated_at = _coerce_datetime(row.get("updated_at"))
        if created_at is not None:
            updates["created_at"] = created_at
        if updated_at is not None:
            updates["updated_at"] = updated_at
        if updates:
            model_cls.objects.filter(pk=pk).update(**updates)

    def _reset_sequences(self, models_list: list[Any]) -> None:
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), models_list)
        if sequence_sql:
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)

    def _migrate_uploads(self, source_dir: Path) -> None:
        if not source_dir.exists():
            msg = f"Uploads directory does not exist: {source_dir}"
            raise CommandError(msg)

        media_root = Path(settings.MEDIA_ROOT)
        target_images_dir = media_root / "images"
        target_images_dir.mkdir(parents=True, exist_ok=True)

        copied = 0
        images_subdir = source_dir / "images"
        search_root = images_subdir if images_subdir.is_dir() else source_dir

        for file_path in search_root.rglob("*"):
            if not file_path.is_file() or file_path.name.startswith("."):
                continue
            rel_path = file_path.relative_to(search_root)
            dest_path = target_images_dir / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_path)
            copied += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Migrated {copied} uploaded file(s) "
                f"from {source_dir} to {target_images_dir}",
            ),
        )
