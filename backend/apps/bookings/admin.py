from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("contact_name", "route", "party_size", "travel_date", "status")
    list_filter = ("status", "travel_date")
    search_fields = ("contact_name", "phone", "route__title")
