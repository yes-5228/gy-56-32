from rest_framework import serializers

from .models import Attraction


class AttractionSerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Attraction
        fields = [
            "id",
            "name",
            "city",
            "category",
            "category_label",
            "duration_hours",
            "ticket_price",
            "highlight",
            "sort_order",
        ]
