from rest_framework import viewsets

from .models import TravelRoute
from .serializers import TravelRouteSerializer


class TravelRouteViewSet(viewsets.ModelViewSet):
    serializer_class = TravelRouteSerializer

    def get_queryset(self):
        queryset = (
            TravelRoute.objects.prefetch_related("stops__attraction", "bookings")
            .all()
        )
        status = self.request.query_params.get("status")
        city = self.request.query_params.get("city")
        if status:
            queryset = queryset.filter(status=status)
        if city:
            queryset = queryset.filter(city__icontains=city)
        return queryset
