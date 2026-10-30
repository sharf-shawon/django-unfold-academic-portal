from http import HTTPStatus

from django.db import connection
from django.db.models import Prefetch
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View

from .forms import ResultSearchForm
from .models import Result
from .models import Student


class HealthCheckView(View):
    """
    Lightweight Coolify & Docker healthcheck endpoint (`GET /healthz/`).
    Verifies SQLite database connectivity (`SELECT 1`) and returns HTTP 200 OK.
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse(
            {"status": "ok", "database": "ok"},
            status=HTTPStatus.OK,
        )


class ResultPublicView(View):
    """
    Public student result search (GET /) and result verification display (POST /).
    Replicates `ResultPublicController@index` and `ResultPublicController@show`
    from the legacy Laravel application.
    """

    index_template_name = "results/index.html"
    show_template_name = "results/show.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        form = ResultSearchForm()
        return render(request, self.index_template_name, {"form": form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = ResultSearchForm(request.POST)
        if not form.is_valid():
            return render(request, self.index_template_name, {"form": form})

        student_id = form.cleaned_data["student_id"]
        date_of_birth = form.cleaned_data["date_of_birth"]

        results_qs = Result.objects.select_related(
            "course",
            "course__semester",
        ).order_by("id")
        student = get_object_or_404(
            Student.objects.prefetch_related(Prefetch("results", queryset=results_qs)),
            student_id=student_id,
            date_of_birth=date_of_birth,
        )
        return render(
            request,
            self.show_template_name,
            {
                "student": student,
                "results": student.results.all(),
            },
        )
