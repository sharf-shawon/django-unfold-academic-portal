# ruff: noqa: PLR2004, E501
from datetime import date
from decimal import Decimal
from http import HTTPStatus
from pathlib import Path

import pytest
import tablib
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from web_result.results.admin import CourseResource
from web_result.results.admin import ResultResource
from web_result.results.admin import SemesterResource
from web_result.results.admin import StudentResource
from web_result.results.models import Course
from web_result.results.models import Result
from web_result.results.models import Semester
from web_result.results.models import Student
from web_result.results.models import StudentCourse

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_every_registered_admin_model_uses_unfold() -> None:
    """Ensure all existing Cookiecutter Django models and new academic models use Unfold."""
    registered_models = list(admin.site._registry.items())  # noqa: SLF001
    assert len(registered_models) >= 9
    for model, model_admin in registered_models:
        assert isinstance(model_admin, UnfoldModelAdmin), (
            f"Admin for {model.__name__} ({type(model_admin)}) does not inherit "
            "from unfold.admin.ModelAdmin"
        )


def test_unfold_admin_pages_render_for_all_models(client: Client) -> None:
    """Verify changelist and add views render cleanly in Unfold for every registered model."""
    call_command("import_legacy_data", seed_demo_user=True)
    user = User.objects.get(email="demo@shawon.me")
    assert user.check_password("demo1234")
    client.force_login(user)

    for model in admin.site._registry:  # noqa: SLF001
        opts = model._meta  # noqa: SLF001
        changelist_url = reverse(f"admin:{opts.app_label}_{opts.model_name}_changelist")
        response = client.get(changelist_url)
        assert response.status_code == HTTPStatus.OK, (
            f"Failed changelist for {opts.label}"
        )

        add_url = reverse(f"admin:{opts.app_label}_{opts.model_name}_add")
        add_response = client.get(add_url)
        assert add_response.status_code == HTTPStatus.OK, (
            f"Failed add view for {opts.label}"
        )


def test_course_delete_works_in_unfold_admin(client: Client) -> None:
    """Verify deleting a Course record works in Django Unfold Admin."""
    call_command("import_legacy_data", seed_demo_user=True)
    user = User.objects.get(email="demo@shawon.me")
    client.force_login(user)

    semester = Semester.objects.create(name="Fall", year="2024")
    course = Course.objects.create(name="Algorithms", code="CSC301", semester=semester)
    delete_url = reverse("admin:results_course_delete", args=[course.pk])

    response = client.post(delete_url, {"post": "yes"})
    assert response.status_code == HTTPStatus.FOUND
    assert not Course.objects.filter(pk=course.pk).exists()


def test_public_result_search_and_verification(
    client: Client,
    tmp_path: Path,
    settings,
) -> None:
    """Verify GET / and POST / public student verification portal and student photo serving."""
    settings.MEDIA_ROOT = str(tmp_path)
    images_dir = tmp_path / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    (images_dir / "student1.png").write_bytes(b"\x89PNG\r\n\x1a\nfake-image")

    semester = Semester.objects.create(name="1st Semester", year="2024")
    course = Course.objects.create(
        name="Computer Fundamentals",
        code="CSE101",
        semester=semester,
    )
    student = Student.objects.create(
        student_id="STD-2024-001",
        name="Alice Rahman",
        email="alice@example.com",
        phone="01700000000",
        address="Dhaka",
        session="2023-2024",
        department="Computer Science",
        date_of_birth=date(2002, 5, 14),
        date_of_issue=date(2024, 6, 1),
        cgpa=Decimal("3.85"),
        image="images/student1.png",
    )
    Result.objects.create(student=student, course=course, gpa=Decimal("3.90"))

    # 1. GET /
    get_resp = client.get(reverse("results:public_index"))
    assert get_resp.status_code == HTTPStatus.OK
    content = get_resp.content.decode()
    assert "Student ID" in content
    assert "Date of Birth" in content
    assert "Search Result" in content

    # 2. POST / with valid student_id and matching date_of_birth
    post_resp = client.post(
        reverse("results:public_index"),
        {"student_id": "STD-2024-001", "date_of_birth": "2002-05-14"},
    )
    assert post_resp.status_code == HTTPStatus.OK
    show_html = post_resp.content.decode()
    assert "Name: Alice Rahman" in show_html
    assert "Student ID: STD-2024-001" in show_html
    assert "Department: Computer Science" in show_html
    assert "Session: 2023-2024" in show_html
    assert "Date of Birth: 2002-05-14" in show_html
    assert "CGPA: 3.85" in show_html
    assert "Date of Issue: 2024-06-01" in show_html
    assert "CSE101" in show_html
    assert "1st Semester" in show_html
    assert "3.90" in show_html
    assert "/uploads/images/student1.png" in show_html

    # 3. Verify /uploads/images/student1.png serves the migrated file
    img_resp = client.get("/uploads/images/student1.png")
    assert img_resp.status_code == HTTPStatus.OK

    # 4. POST / with unknown student_id returns form error
    invalid_resp = client.post(
        reverse("results:public_index"),
        {"student_id": "UNKNOWN-ID", "date_of_birth": "2002-05-14"},
    )
    assert invalid_resp.status_code == HTTPStatus.OK
    assert "The selected student id is invalid." in invalid_resp.content.decode()

    # 5. POST / with valid student_id but wrong date_of_birth returns 404
    wrong_dob_resp = client.post(
        reverse("results:public_index"),
        {"student_id": "STD-2024-001", "date_of_birth": "1999-01-01"},
    )
    assert wrong_dob_resp.status_code == HTTPStatus.NOT_FOUND


def test_import_legacy_data_sql_dump_and_uploads(tmp_path: Path, settings) -> None:
    """Verify `import_legacy_data` imports MySQL dumps and migrates uploaded pictures."""
    media_root = tmp_path / "media"
    settings.MEDIA_ROOT = str(media_root)

    legacy_uploads = tmp_path / "old_uploads" / "images"
    legacy_uploads.mkdir(parents=True)
    (legacy_uploads / "photo_legacy.jpg").write_bytes(b"fake-jpeg-bytes")

    sql_dump = tmp_path / "dump.sql"
    sql_dump.write_text(
        """
        INSERT INTO `users` (`id`, `name`, `email`, `password`) VALUES
        (99, 'OldUser', 'old@example.com', 'hashed');

        INSERT INTO `semesters` (`id`, `name`, `year`, `created_at`, `updated_at`) VALUES
        (10, 'Spring', '2023', '2024-03-17 08:00:00', '2024-03-17 08:00:00');

        INSERT INTO `courses` (`id`, `name`, `code`, `semester_id`, `created_at`, `updated_at`) VALUES
        (20, 'Data Structures', 'CSC201', 10, '2024-03-17 08:10:00', '2024-03-17 08:10:00');

        INSERT INTO `students` (`id`, `student_id`, `name`, `email`, `phone`, `address`, `session`, `department`, `date_of_birth`, `date_of_issue`, `cgpa`, `image`, `created_at`, `updated_at`) VALUES
        (30, 'BITI-1001', 'Karim Ahmed', 'karim@example.com', '01811112222', 'Chittagong', '2022-23', 'CSE', '2001-11-20', '2024-01-15', 3.75, 'images/photo_legacy.jpg', '2024-03-17 08:20:00', '2024-03-17 08:20:00');

        INSERT INTO `course_student` (`course_id`, `student_id`) VALUES
        (20, 30);

        INSERT INTO `results` (`id`, `course_id`, `student_id`, `gpa`, `created_at`, `updated_at`) VALUES
        (40, 20, 30, '3.75', '2024-03-17 08:30:00', '2024-03-17 08:30:00');
        """,
        encoding="utf-8",
    )

    call_command(
        "import_legacy_data",
        sql_file=str(sql_dump),
        uploads_dir=str(tmp_path / "old_uploads"),
        seed_demo_user=True,
    )

    # Legacy users row was skipped, demo user was seeded
    assert not User.objects.filter(email="old@example.com").exists()
    assert User.objects.filter(email="demo@shawon.me").exists()

    # Academic records imported with exact IDs & relationships
    semester = Semester.objects.get(id=10)
    assert semester.name == "Spring"
    assert semester.year == "2023"

    course = Course.objects.get(id=20)
    assert course.code == "CSC201"
    assert course.semester_id == 10

    student = Student.objects.get(id=30)
    assert student.student_id == "BITI-1001"
    assert student.cgpa == Decimal("3.75")
    assert student.image_url == "/uploads/images/photo_legacy.jpg"
    assert StudentCourse.objects.filter(course_id=20, student_id=30).exists()

    result = Result.objects.get(id=40)
    assert result.student_id == 30
    assert result.course_id == 20
    assert result.gpa == Decimal("3.75")

    # Uploaded image file was copied into MEDIA_ROOT/images/photo_legacy.jpg
    assert (
        media_root / "images" / "photo_legacy.jpg"
    ).read_bytes() == b"fake-jpeg-bytes"


def test_django_import_export_resources() -> None:
    """Verify browser import/export resources for Semester, Course, Student, and Result."""
    sem_dataset = tablib.Dataset(
        headers=["id", "name", "year"],
    )
    sem_dataset.append([1, "Summer", "2024"])
    SemesterResource().import_data(sem_dataset, dry_run=False)
    assert Semester.objects.filter(id=1, name="Summer", year="2024").exists()

    course_dataset = tablib.Dataset(
        headers=["id", "name", "code", "semester_id"],
    )
    course_dataset.append([2, "Operating Systems", "CSE305", 1])
    CourseResource().import_data(course_dataset, dry_run=False)
    assert Course.objects.filter(id=2, code="CSE305", semester_id=1).exists()

    student_dataset = tablib.Dataset(
        headers=[
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
        ],
    )
    student_dataset.append(
        [
            3,
            "S-300",
            "Nadia Islam",
            "nadia@example.com",
            "01900000000",
            "Sylhet",
            "2024",
            "EEE",
            "2003-03-03",
            "2024-09-01",
            "4.00",
            "",
        ],
    )
    StudentResource().import_data(student_dataset, dry_run=False)
    assert Student.objects.filter(id=3, student_id="S-300").exists()

    result_dataset = tablib.Dataset(
        headers=["id", "course_id", "student_id", "gpa"],
    )
    result_dataset.append([4, 2, 3, "4.00"])
    ResultResource().import_data(result_dataset, dry_run=False)
    assert Result.objects.filter(
        id=4,
        course_id=2,
        student_id=3,
        gpa=Decimal("4.00"),
    ).exists()


def test_healthz_endpoint_exempt_from_ssl_redirect(client: Client, settings) -> None:
    """Verify GET /healthz/ returns 200 OK JSON even when SECURE_SSL_REDIRECT is True."""
    settings.SECURE_SSL_REDIRECT = True
    settings.SECURE_REDIRECT_EXEMPT = [r"^healthz/?$"]

    response = client.get("/healthz/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok", "database": "ok"}


def test_coolify_magic_env_hosts_and_origins_resolution() -> None:
    """Verify Coolify magic env vars populate ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS."""
    from config.settings.production import build_coolify_hosts_and_origins  # noqa: PLC0415

    hosts, origins, secure_cookies = build_coolify_hosts_and_origins(
        {
            "SERVICE_FQDN_DJANGO": "results.example.com",
            "SERVICE_FQDN_DJANGO_5000": "results.example.com:5000",
            "SERVICE_URL_DJANGO": "https://results.example.com",
            "SERVICE_URL_DJANGO_5000": "https://results.example.com:5000",
            "COOLIFY_FQDN": "results.example.com,portal.example.org:5000",
            "COOLIFY_URL": "https://results.example.com,https://portal.example.org:5000",
        },
    )
    assert "results.example.com" in hosts
    assert "portal.example.org" in hosts
    assert "localhost" in hosts
    assert "127.0.0.1" in hosts
    assert all(":" not in h for h in hosts if not h.startswith("["))
    assert "https://results.example.com" in origins
    assert "https://portal.example.org" in origins
    assert secure_cookies is True

    # Verify HTTP-only initial wildcard domain (e.g. sslip.io before SSL) disables secure cookies
    _, http_origins, http_secure = build_coolify_hosts_and_origins(
        {
            "SERVICE_FQDN_DJANGO": "app.127.0.0.1.sslip.io",
            "SERVICE_URL_DJANGO": "http://app.127.0.0.1.sslip.io",
        },
    )
    assert "http://app.127.0.0.1.sslip.io" in http_origins
    assert http_secure is False


def test_backup_data_create_prune_and_restore(tmp_path: Path, settings) -> None:
    """Verify online SQLite + media backup creation, retention pruning, and restore."""
    import sqlite3  # noqa: PLC0415

    db_file = tmp_path / "data" / "db.sqlite3"
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file))
    conn.execute("CREATE TABLE sample_items (id INTEGER PRIMARY KEY, label TEXT)")
    conn.execute("INSERT INTO sample_items (id, label) VALUES (1, 'initial-state')")
    conn.commit()
    conn.close()

    media_dir = tmp_path / "media"
    (media_dir / "images").mkdir(parents=True, exist_ok=True)
    (media_dir / "images" / "test.jpg").write_bytes(b"original-image")

    backups_dir = tmp_path / "backups"
    settings.MEDIA_ROOT = str(media_dir)
    settings.DATA_DIR = db_file.parent

    archive_1 = call_command(
        "backup_data",
        db_path=str(db_file),
        output_dir=str(backups_dir),
        keep=2,
    )
    assert Path(archive_1).exists()
    assert (db_file.parent / "backups" / "latest.tar.gz").exists()

    # Create two more backups with keep=2 and verify oldest is pruned
    call_command(
        "backup_data",
        db_path=str(db_file),
        output_dir=str(backups_dir),
        keep=2,
    )
    archive_3 = call_command(
        "backup_data",
        db_path=str(db_file),
        output_dir=str(backups_dir),
        keep=2,
    )
    remaining = list(backups_dir.glob("web-result-backup-*.tar.gz"))
    assert len(remaining) == 2

    # Mutate database and media, then restore from archive_3
    conn = sqlite3.connect(str(db_file))
    conn.execute("DELETE FROM sample_items")
    conn.commit()
    conn.close()
    (media_dir / "images" / "test.jpg").write_bytes(b"corrupted-image")

    call_command("backup_data", db_path=str(db_file), restore=str(archive_3))

    conn = sqlite3.connect(str(db_file))
    rows = conn.execute("SELECT label FROM sample_items WHERE id = 1").fetchall()
    conn.close()
    assert rows == [("initial-state",)]
    assert (media_dir / "images" / "test.jpg").read_bytes() == b"original-image"


def test_coolify_docker_compose_yaml_structure(settings) -> None:
    """Verify /docker-compose.yaml is Coolify-ready with single django service and healthcheck."""
    import yaml  # noqa: PLC0415

    base_dir = Path(settings.BASE_DIR)
    compose_path = base_dir / "docker-compose.yaml"
    prod_compose_path = base_dir / "docker-compose.production.yml"
    env_example_path = base_dir / ".env.example"

    assert compose_path.exists()
    assert prod_compose_path.exists()
    assert env_example_path.exists()

    parsed = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    assert list(parsed["services"].keys()) == ["django"]
    django_svc = parsed["services"]["django"]
    assert "image" not in django_svc
    assert "ports" not in django_svc
    assert "5000" in [str(p) for p in django_svc.get("expose", [])]
    assert "healthcheck" in django_svc
    assert "http://127.0.0.1:5000/healthz/" in django_svc["healthcheck"]["test"]

    env_list = "\n".join(str(item) for item in django_svc.get("environment", []))
    assert "SERVICE_FQDN_DJANGO_5000" in env_list
    assert "SERVICE_BASE64_64_DJANGO" in env_list
    assert {"sqlite-data", "media-data", "backups-data"} <= set(
        parsed["volumes"].keys(),
    )


def test_readme_documents_portfolio_and_agent_reference(settings) -> None:
    """Verify README.md documents portfolio keywords, AI migration, backup, and Coolify config."""
    readme_path = Path(settings.BASE_DIR) / "README.md"
    assert readme_path.exists()
    content = readme_path.read_text(encoding="utf-8")

    for required_token in (
        "django-unfold-academic-portal",
        "2 Prompts",
        "OpenSpec",
        "Context7",
        "import_legacy_data",
        "backup_data",
        "SERVICE_FQDN_DJANGO_5000",
        "SERVICE_BASE64_64_DJANGO",
        "/healthz/",
    ):
        assert required_token in content
