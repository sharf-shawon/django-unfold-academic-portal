from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from import_export import fields
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
from unfold.contrib.import_export.forms import ExportForm
from unfold.contrib.import_export.forms import ImportForm

from .models import Course
from .models import Result
from .models import Semester
from .models import Student
from .models import StudentCourse


class SemesterResource(resources.ModelResource):
    class Meta:
        model = Semester
        import_id_fields = ("id",)
        fields = ("id", "name", "year", "created_at", "updated_at")
        export_order = ("id", "name", "year", "created_at", "updated_at")


class CourseResource(resources.ModelResource):
    semester_id = fields.Field(
        column_name="semester_id",
        attribute="semester",
        widget=ForeignKeyWidget(Semester, field="id"),
    )

    class Meta:
        model = Course
        import_id_fields = ("id",)
        fields = ("id", "name", "code", "semester_id", "created_at", "updated_at")
        export_order = ("id", "name", "code", "semester_id", "created_at", "updated_at")


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ("id",)
        fields = (
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
        )
        export_order = fields


class ResultResource(resources.ModelResource):
    course_id = fields.Field(
        column_name="course_id",
        attribute="course",
        widget=ForeignKeyWidget(Course, field="id"),
    )
    student_id = fields.Field(
        column_name="student_id",
        attribute="student",
        widget=ForeignKeyWidget(Student, field="id"),
    )

    class Meta:
        model = Result
        import_id_fields = ("id",)
        fields = (
            "id",
            "course_id",
            "student_id",
            "gpa",
            "created_at",
            "updated_at",
        )
        export_order = fields


class CourseInline(TabularInline):
    model = Course
    extra = 0
    fields = ("code", "name")
    show_change_link = True


class ResultInline(TabularInline):
    model = Result
    extra = 0
    fields = ("course", "gpa")
    autocomplete_fields = ("course",)
    show_change_link = True


class StudentCourseInline(TabularInline):
    model = StudentCourse
    extra = 0
    fields = ("course",)
    autocomplete_fields = ("course",)


@admin.register(Semester)
class SemesterAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_classes = [SemesterResource]
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ("id", "name", "year", "created_at")
    list_display_links = ("id", "name")
    list_filter = ("year",)
    search_fields = ("name", "year")
    ordering = ("id",)
    inlines = [CourseInline]


@admin.register(Course)
class CourseAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_classes = [CourseResource]
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ("id", "code", "name", "semester", "created_at")
    list_display_links = ("id", "code", "name")
    list_filter = ("semester",)
    search_fields = ("code", "name", "semester__name", "semester__year")
    autocomplete_fields = ("semester",)
    ordering = ("id",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Course]:
        return super().get_queryset(request).select_related("semester")


@admin.register(Student)
class StudentAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_classes = [StudentResource]
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = (
        "id",
        "student_id",
        "name",
        "email",
        "phone",
        "department",
        "session",
        "date_of_birth",
        "cgpa",
        "image_preview",
    )
    list_display_links = ("id", "student_id", "name")
    list_filter = ("department", "session")
    search_fields = ("student_id", "name", "email", "phone", "department", "session")
    readonly_fields = ("image_preview", "created_at", "updated_at")
    ordering = ("id",)
    inlines = [ResultInline, StudentCourseInline]
    fieldsets = (
        (
            _("Student Identity"),
            {
                "fields": (
                    "student_id",
                    "name",
                    "email",
                    "phone",
                    "address",
                ),
            },
        ),
        (
            _("Academic Information"),
            {
                "fields": (
                    "department",
                    "session",
                    "cgpa",
                    "date_of_birth",
                    "date_of_issue",
                ),
            },
        ),
        (
            _("Student Photograph"),
            {
                "fields": (
                    "image",
                    "image_preview",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Photo"))
    def image_preview(self, obj: Student) -> str:
        if obj.image:
            return format_html(
                '<img src="{}" alt="{}" '
                'style="max-height: 48px; border-radius: 6px;" />',
                obj.image_url,
                obj.name,
            )
        return "-"


@admin.register(Result)
class ResultAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_classes = [ResultResource]
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = (
        "id",
        "student_roll",
        "student_name",
        "course_display",
        "semester_display",
        "gpa",
    )
    list_display_links = ("id", "student_roll")
    list_filter = ("course__semester", "course")
    search_fields = (
        "student__student_id",
        "student__name",
        "course__code",
        "course__name",
        "course__semester__name",
    )
    autocomplete_fields = ("student", "course")
    ordering = ("id",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Result]:
        return (
            super()
            .get_queryset(request)
            .select_related("student", "course", "course__semester")
        )

    @admin.display(description=_("Student ID"), ordering="student__student_id")
    def student_roll(self, obj: Result) -> str:
        return obj.student.student_id

    @admin.display(description=_("Student Name"), ordering="student__name")
    def student_name(self, obj: Result) -> str:
        return obj.student.name

    @admin.display(description=_("Course"), ordering="course__code")
    def course_display(self, obj: Result) -> str:
        return f"{obj.course.code} - {obj.course.name}"

    @admin.display(description=_("Semester"), ordering="course__semester__name")
    def semester_display(self, obj: Result) -> str:
        return obj.course.semester.name
