from django.shortcuts import render
import uuid

from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from accounts.mixins import OrganizationRequiredMixin
from bookings.models import Ticket
from events.models import Event
from .forms import SlotForm
from .services import organization_analytics

EVENT_FIELDS = ["title", "description", "event_type", "location", "is_active"]


class OrgEventListView(OrganizationRequiredMixin, ListView):
    template_name = "dashboard/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        return (
            Event.objects.filter(organization=self.request.user.organization)
            .annotate(slot_count=Count("slots"))
            .order_by("-created_at")
        )


class OrgEventCreateView(OrganizationRequiredMixin, CreateView):
    model = Event
    fields = EVENT_FIELDS
    template_name = "dashboard/event_form.html"

    def form_valid(self, form):
        form.instance.organization = self.request.user.organization
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("org_event_detail", kwargs={"pk": self.object.pk})


class OrgEventUpdateView(OrganizationRequiredMixin, UpdateView):
    fields = EVENT_FIELDS
    template_name = "dashboard/event_form.html"

    def get_queryset(self):
        return Event.objects.filter(organization=self.request.user.organization)

    def get_success_url(self):
        return reverse("org_event_detail", kwargs={"pk": self.object.pk})


class OrgEventDetailView(OrganizationRequiredMixin, DetailView):
    template_name = "dashboard/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.filter(organization=self.request.user.organization)


class OrgSlotCreateView(OrganizationRequiredMixin, CreateView):
    form_class = SlotForm
    template_name = "dashboard/slot_form.html"

    def get_event(self):
        return get_object_or_404(
            Event,
            pk=self.kwargs["event_pk"],
            organization=self.request.user.organization,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.get_event()
        return context

    def form_valid(self, form):
        form.instance.event = self.get_event()
        form.instance.seats_left = form.cleaned_data["capacity"]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("org_event_detail", kwargs={"pk": self.kwargs["event_pk"]})
# Create your views here.
class OrgTicketListView(OrganizationRequiredMixin, ListView):
    template_name = "dashboard/tickets.html"
    context_object_name = "tickets"

    def get_queryset(self):
        tickets = (
            Ticket.objects.filter(
                booking__slot__event__organization=self.request.user.organization
            )
            .select_related("booking__user", "booking__slot__event")
            .order_by("-booking__created_at")
        )
        self.status = self.request.GET.get("status", "active")
        if self.status in (Ticket.ACTIVE, Ticket.CONSUMED):
            tickets = tickets.filter(status=self.status)

        self.query = self.request.GET.get("q", "").strip()
        if self.query:
            try:
                tickets = tickets.filter(ticket_id=uuid.UUID(self.query))
            except ValueError:
                tickets = tickets.none()
        return tickets

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.status
        context["query"] = self.query
        return context


class OrgTicketConsumeView(OrganizationRequiredMixin, View):
    def post(self, request, pk):
        organization = request.user.organization
        with transaction.atomic():
            ticket = get_object_or_404(
                Ticket.objects.select_for_update(of=("self",)).filter(
                    booking__slot__event__organization=organization
                ),
                pk=pk,
            )
            if ticket.status == Ticket.CONSUMED:
                messages.warning(request, "This ticket was already consumed.")
            else:
                ticket.status = Ticket.CONSUMED
                ticket.consumed_at = timezone.now()
                ticket.save(update_fields=["status", "consumed_at"])
                messages.success(request, "Ticket marked as consumed.")
        return redirect("org_tickets")
class OrgAnalyticsView(OrganizationRequiredMixin, TemplateView):
    template_name = "dashboard/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(organization_analytics(self.request.user.organization))
        return context