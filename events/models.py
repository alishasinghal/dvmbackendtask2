from django.db import models
from accounts.models import OrganizationProfile


class Event(models.Model):
    SLOT = "slot"
    TICKET = "ticket"
    EVENT_TYPES = [(SLOT, "Slot-based"), (TICKET, "Ticket-based")]

    organization = models.ForeignKey(
        OrganizationProfile, on_delete=models.CASCADE, related_name="events"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Slot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="slots")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.PositiveIntegerField()
    seats_left = models.PositiveIntegerField()
    @property
    def booked(self):
        return self.capacity - self.seats_left

    class Meta:
        ordering = ["start_time"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="slot_end_after_start",
            ),
            models.CheckConstraint(
                condition=models.Q(seats_left__lte=models.F("capacity")),
                name="slot_seats_within_capacity",
            ),
        ]

    def __str__(self):
        return f"{self.event.title} @ {self.start_time:%d %b %H:%M}"