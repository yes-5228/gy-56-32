from django.contrib import admin

from .models import RouteStop, TravelRoute


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1


@admin.register(TravelRoute)
class TravelRouteAdmin(admin.ModelAdmin):
    list_display = ("title", "city", "days", "status", "min_group_size", "max_group_size")
    list_filter = ("status", "city")
    search_fields = ("title", "city")
    inlines = [RouteStopInline]
