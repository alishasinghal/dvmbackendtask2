from django.urls import path

from . import views

urlpatterns = [
    path("wallet/", views.WalletView.as_view(), name="wallet"),
    path("book/<int:slot_id>/", views.BookSlotView.as_view(), name="book_slot"),
    path("transactions/", views.TransactionListView.as_view(), name="transactions"),
    path("bookings/", views.MyBookingsView.as_view(), name="my_bookings"),
    path("tickets/", views.MyTicketsView.as_view(), name="my_tickets"),
]