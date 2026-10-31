from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView

from accounts.mixin import GroupRequiredMixin
from events.models import Slot
from .forms import AddMoneyForm, BookingForm
from .models import Booking, Ticket, Transaction
from .services import BookingError, add_money, book_slot


class WalletView(GroupRequiredMixin, View):
    group_name = "Customer"

    def get(self, request):
        return self.show(request, AddMoneyForm())

    def post(self, request):
        form = AddMoneyForm(request.POST)
        if form.is_valid():
            try:
                add_money(request.user, form.cleaned_data["amount"])
            except BookingError as error:
                messages.error(request, str(error))
            else:
                messages.success(request, "Money added to your wallet.")
                return redirect("wallet")
        return self.show(request, form)

    def show(self, request, form):
        balance = request.user.wallet.balance
        return render(request, "bookings/wallet.html", {"form": form, "balance": balance})


class BookSlotView(GroupRequiredMixin, View):
    group_name = "Customer"

    def post(self, request, slot_id):
        slot = get_object_or_404(Slot, pk=slot_id)
        form = BookingForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Please enter a valid quantity (1 to 10).")
            return redirect("event_detail", pk=slot.event_id)
        try:
            book_slot(request.user, slot_id, form.cleaned_data["quantity"])
        except BookingError as error:
            messages.error(request, str(error))
            return redirect("event_detail", pk=slot.event_id)
        messages.success(request, "Booking confirmed!")
        return redirect("my_tickets")


class TransactionListView(GroupRequiredMixin, ListView):
    group_name = "Customer"
    template_name = "bookings/transactions.html"
    context_object_name = "transactions"

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related(
            "booking__slot__event"
        )


class MyBookingsView(GroupRequiredMixin, ListView):
    group_name = "Customer"
    template_name = "bookings/my_bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return (
            Booking.objects.filter(user=self.request.user)
            .select_related("slot__event")
            .prefetch_related("tickets")
            .order_by("-created_at")
        )


class MyTicketsView(GroupRequiredMixin, ListView):
    group_name = "Customer"
    template_name = "bookings/my_tickets.html"
    context_object_name = "tickets"

    def get_queryset(self):
        return (
            Ticket.objects.filter(booking__user=self.request.user, status=Ticket.ACTIVE)
            .select_related("booking__slot__event")
            .order_by("booking__slot__start_time")
        )
# Create your views here.
