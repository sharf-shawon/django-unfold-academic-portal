from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.views.static import serve

from web_result.results.views import HealthCheckView
from web_result.results.views import ResultPublicView


def serve_media(request, path: str):
    return serve(request, path, document_root=settings.MEDIA_ROOT)


urlpatterns = [
    path("", ResultPublicView.as_view(), name="home"),
    path("healthz/", HealthCheckView.as_view(), name="healthz"),
    path("", include("web_result.results.urls", namespace="results")),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("web_result.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
]

if getattr(settings, "SERVE_MEDIA", False) or settings.DEBUG:
    urlpatterns += [
        re_path(r"^uploads/(?P<path>.*)$", serve_media),
        re_path(r"^media/(?P<path>.*)$", serve_media),
    ]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
