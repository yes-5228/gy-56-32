from rest_framework import serializers

from .models import TravelNotice


class TravelNoticeSerializer(serializers.ModelSerializer):
    route_title = serializers.CharField(source="route.title", read_only=True)
    notice_type_label = serializers.CharField(source="get_notice_type_display", read_only=True)

    class Meta:
        model = TravelNotice
        fields = [
            "id",
            "route",
            "route_title",
            "notice_type",
            "notice_type_label",
            "title",
            "content",
            "publish_at",
            "is_sent",
            "created_at",
        ]
