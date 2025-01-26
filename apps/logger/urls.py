from django.urls import path

from apps.logger.views.auditlog import AdminDashboardView

urlpatterns = [
    path("admin-dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
]
