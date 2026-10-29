from django.urls import path

from . import views

urlpatterns = [
    path("", views.OrgEventListView.as_view(), name="org_dashboard"),
    path("events/new/", views.OrgEventCreateView.as_view(), name="org_event_create"),
    path("events/<int:pk>/", views.OrgEventDetailView.as_view(), name="org_event_detail"),
    path("events/<int:pk>/edit/", views.OrgEventUpdateView.as_view(), name="org_event_update"),
    path("events/<int:event_pk>/slots/new/", views.OrgSlotCreateView.as_view(), name="org_slot_create"),
    path("tickets/", views.OrgTicketListView.as_view(), name="org_tickets"),
    path("tickets/<int:pk>/consume/", views.OrgTicketConsumeView.as_view(), name="org_ticket_consume"),
    path("analytics/", views.OrgAnalyticsView.as_view(), name="org_analytics"),
]