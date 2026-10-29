from django.urls import path

from . import views

urlpatterns = [
    path("events/", views.EventListView.as_view(), name="event_list"),
    path("events/<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
]