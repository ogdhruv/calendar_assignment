from django.urls import path
from calendarAPI import views

urlpatterns = [
    path("rest/v1/calendar/init/", views.GoogleCalendarInitView.as_view(), name="access"),
    path(
        "rest/v1/calendar/redirect/",
        views.GoogleCalendarRedirectView.as_view(),
        name="redirect",
    ),
]
