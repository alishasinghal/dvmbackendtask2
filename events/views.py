from django.shortcuts import render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from accounts.mixin import GroupRequiredMixin
from .models import Event


class EventListView(GroupRequiredMixin, ListView):
    group_name = "Customer"
    template_name = "events/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        return Event.objects.filter(is_active=True).select_related("organization")


class EventDetailView(GroupRequiredMixin, DetailView):
    group_name = "Customer"
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slots"] = self.object.slots.filter(start_time__gt=timezone.now())
        return context
# Create your views here.
