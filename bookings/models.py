import uuid
from django.conf import settings
from django.db import models
from events.models import Slot


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bookings"
    )
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0), name="booking_quantity_positive"
            )
        ]
    slot = models.ForeignKey(Slot, on_delete=models.PROTECT, related_name="bookings")
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
   


class Ticket(models.Model):
    ACTIVE = "active"
    CONSUMED = "consumed"
    STATUS = [(ACTIVE, "Active"), (CONSUMED, "Consumed")]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="tickets")
    ticket_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=STATUS, default=ACTIVE)
    consumed_at = models.DateTimeField(null=True, blank=True)


class Transaction(models.Model):
    CREDIT = "credit"
    DEBIT = "debit"
    TYPES = [(CREDIT, "Money added"), (DEBIT, "Booking payment")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPES)
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]