from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024  # 2048 KB as in legacy StudentController


def validate_image_size(value) -> None:
    """Validate uploaded student image does not exceed 2MB."""
    if value and hasattr(value, "size") and value.size > MAX_IMAGE_SIZE_BYTES:
        msg = _("Image file size must not exceed 2 MB.")
        raise ValidationError(msg)


class Semester(models.Model):
    name = models.CharField(_("Name"), max_length=20)
    year = models.CharField(
        _("Year"),
        max_length=4,
        validators=[
            RegexValidator(
                regex=r"^\d{4}$",
                message=_("Year must be a 4-digit number."),
            ),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "semesters"
        ordering = ["id"]
        verbose_name = _("Semester")
        verbose_name_plural = _("Semesters")

    def __str__(self) -> str:
        return f"{self.name} ({self.year})"


class Course(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    code = models.CharField(_("Code"), max_length=255)
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="courses",
        db_column="semester_id",
        verbose_name=_("Semester"),
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "courses"
        ordering = ["id"]
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Student(models.Model):
    student_id = models.CharField(_("Student ID"), max_length=255, unique=True)
    name = models.CharField(_("Name"), max_length=255)
    email = models.EmailField(_("Email"), max_length=255, unique=True)
    phone = models.CharField(_("Phone"), max_length=255)
    address = models.CharField(_("Address"), max_length=255)
    session = models.CharField(_("Session"), max_length=255)
    department = models.CharField(_("Department"), max_length=255)
    date_of_birth = models.DateField(_("Date of Birth"))
    date_of_issue = models.DateField(_("Date of Issue"))
    cgpa = models.DecimalField(
        _("CGPA"),
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("4.00")),
        ],
    )
    image = models.FileField(
        _("Image"),
        upload_to="images/",
        max_length=255,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpeg", "png", "jpg", "gif", "svg"],
            ),
            validate_image_size,
        ],
    )
    courses = models.ManyToManyField(
        Course,
        through="StudentCourse",
        related_name="students",
        blank=True,
        verbose_name=_("Courses"),
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "students"
        ordering = ["id"]
        verbose_name = _("Student")
        verbose_name_plural = _("Students")

    def __str__(self) -> str:
        return f"{self.student_id} - {self.name}"

    @property
    def image_url(self) -> str:
        """Return resolved URL for student image (`images/...` compatible)."""
        if not self.image:
            return ""
        raw_name = str(self.image.name).lstrip("/")
        if raw_name.startswith("uploads/"):
            raw_name = raw_name[len("uploads/") :]
        media_prefix = settings.MEDIA_URL.rstrip("/")
        return f"{media_prefix}/{raw_name}"


class StudentCourse(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        db_column="course_id",
        verbose_name=_("Course"),
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        db_column="student_id",
        verbose_name=_("Student"),
    )

    class Meta:
        db_table = "course_student"
        unique_together = (("course", "student"),)
        verbose_name = _("Student Course Enrollment")
        verbose_name_plural = _("Student Course Enrollments")

    def __str__(self) -> str:
        return f"{self.student_id} -> {self.course_id}"


class Result(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="results",
        db_column="course_id",
        verbose_name=_("Course"),
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="results",
        db_column="student_id",
        verbose_name=_("Student"),
    )
    gpa = models.DecimalField(
        _("GPA"),
        max_digits=3,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("4.00")),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "results"
        ordering = ["id"]
        verbose_name = _("Result")
        verbose_name_plural = _("Results")

    def __str__(self) -> str:
        return f"{self.student.student_id} - {self.course.code}: {self.gpa}"

    @property
    def semester(self) -> Semester:
        return self.course.semester
