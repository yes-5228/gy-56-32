from rest_framework import viewsets

from .models import TravelNotice
from .serializers import TravelNoticeSerializer


class TravelNoticeViewSet(viewsets.ModelViewSet):
    serializer_class = TravelNoticeSerializer

    def get_queryset(self):
        queryset = TravelNotice.objects.select_related("route").all()
        route_id = self.request.query_params.get("route")
        notice_type = self.request.query_params.get("notice_type")
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if notice_type:
            queryset = queryset.filter(notice_type=notice_type)
        return queryset
