from django.urls import path
from .views import DashboardsView



urlpatterns = [
    path(
        "",
        DashboardsView.as_view(template_name="new_dashboard_analytics.html"),
        name="index",
    )
]
