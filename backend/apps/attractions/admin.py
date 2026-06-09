from django.contrib import admin

from .models import Attraction


@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "category", "duration_hours", "ticket_price")
    list_filter = ("city", "category")
    search_fields = ("name", "city")
