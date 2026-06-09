from django.contrib import admin

from .models import TravelNotice


@admin.register(TravelNotice)
class TravelNoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "route", "notice_type", "publish_at", "is_sent")
    list_filter = ("notice_type", "is_sent")
    search_fields = ("title", "route__title")
