from django.contrib import admin
from .models import Booking, Ticket, Transaction

admin.site.register(Booking)
admin.site.register(Ticket)
admin.site.register(Transaction)