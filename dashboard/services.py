from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.utils import timezone

from bookings.models import Booking, Ticket
from events.models import Event, Slot


def organization_analytics(organization):
    bookings = Booking.objects.filter(slot__event__organization=organization)
    tickets = Ticket.objects.filter(booking__slot__event__organization=organization)
    slots = Slot.objects.filter(event__organization=organization)

    booking_totals = bookings.aggregate(revenue=Sum("total_price"), count=Count("id"))
    ticket_totals = tickets.aggregate(
        sold=Count("id"),
        consumed=Count("id", filter=Q(status=Ticket.CONSUMED)),
    )
    seat_totals = slots.aggregate(capacity=Sum("capacity"))
    week_ago = timezone.now() - timedelta(days=7)
    last_week = bookings.filter(created_at__gte=week_ago).aggregate(
        revenue=Sum("total_price")
    )

    sold = ticket_totals["sold"] or 0
    consumed = ticket_totals["consumed"] or 0
    capacity = seat_totals["capacity"] or 0
    summary = {
        "revenue": booking_totals["revenue"] or Decimal("0"),
        "revenue_last_7_days": last_week["revenue"] or Decimal("0"),
        "bookings": booking_totals["count"] or 0,
        "tickets_sold": sold,
        "tickets_consumed": consumed,
        "tickets_active": sold - consumed,
        "capacity": capacity,
        "fill_rate": round(100 * sold / capacity) if capacity else 0,
    }

    # Separate grouped queries, merged in Python, to avoid double-counting
    # that happens when you aggregate across several joins at once.
    sales = {
        row["slot__event_id"]: row
        for row in bookings.values("slot__event_id").annotate(
            tickets=Sum("quantity"), revenue=Sum("total_price")
        ).order_by()
    }
    consumed_by_event = {
        row["booking__slot__event_id"]: row["n"]
        for row in tickets.filter(status=Ticket.CONSUMED)
        .values("booking__slot__event_id")
        .annotate(n=Count("id"))
        .order_by()
    }
    capacity_by_event = {
        row["event_id"]: row["capacity"]
        for row in slots.values("event_id").annotate(capacity=Sum("capacity")).order_by()
    }

    rows = []
    for event in Event.objects.filter(organization=organization).order_by("title"):
        sale = sales.get(event.id, {})
        event_sold = sale.get("tickets") or 0
        event_capacity = capacity_by_event.get(event.id, 0)
        rows.append({
            "event": event,
            "tickets_sold": event_sold,
            "consumed": consumed_by_event.get(event.id, 0),
            "revenue": sale.get("revenue") or Decimal("0"),
            "capacity": event_capacity,
            "fill_rate": round(100 * event_sold / event_capacity) if event_capacity else 0,
        })
    rows.sort(key=lambda row: row["revenue"], reverse=True)
    return {"summary": summary, "rows": rows}