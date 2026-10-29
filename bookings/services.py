from django.db import transaction
from django.utils import timezone

from accounts.models import Wallet
from events.models import Slot
from .models import Booking, Ticket, Transaction


class BookingError(Exception):
    """A problem we can safely show to the user."""


@transaction.atomic
def add_money(user, amount):
    if amount <= 0:
        raise BookingError("Amount must be positive.")
    wallet = Wallet.objects.select_for_update().get(user=user)
    wallet.balance += amount
    wallet.save()
    Transaction.objects.create(
        user=user, amount=amount, type=Transaction.CREDIT,
        balance_after=wallet.balance,
    )
    return wallet


@transaction.atomic
def book_slot(user, slot_id, quantity):
    if quantity < 1:
        raise BookingError("Quantity must be at least 1.")

    # Lock rows in a fixed order (slot first, then wallet) to avoid deadlocks.
    try:
        slot = Slot.objects.select_for_update().get(pk=slot_id)
    except Slot.DoesNotExist:
        raise BookingError("This slot does not exist.")
    wallet = Wallet.objects.select_for_update().get(user=user)

    if not slot.event.is_active:
        raise BookingError("This event is not available.")
    if slot.start_time <= timezone.now():
        raise BookingError("This slot has already started.")
    if slot.seats_left < quantity:
        raise BookingError("Not enough seats left.")
    total = slot.price * quantity
    if wallet.balance < total:
        raise BookingError("Insufficient wallet balance.")

    slot.seats_left -= quantity
    slot.save()
    wallet.balance -= total
    wallet.save()

    booking = Booking.objects.create(
        user=user, slot=slot, quantity=quantity, total_price=total
    )
    Ticket.objects.bulk_create([Ticket(booking=booking) for _ in range(quantity)])
    Transaction.objects.create(
        user=user, amount=total, type=Transaction.DEBIT,
        booking=booking, balance_after=wallet.balance,
    )
    return booking