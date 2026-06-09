from rest_framework import viewsets

from .models import Attraction
from .serializers import AttractionSerializer


class AttractionViewSet(viewsets.ModelViewSet):
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        city = self.request.query_params.get("city")
        category = self.request.query_params.get("category")
        if city:
            queryset = queryset.filter(city__icontains=city)
        if category:
            queryset = queryset.filter(category=category)
        return queryset
