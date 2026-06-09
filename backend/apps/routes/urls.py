from rest_framework.routers import DefaultRouter

from .views import TravelRouteViewSet

router = DefaultRouter()
router.register("", TravelRouteViewSet, basename="travel-route")

urlpatterns = router.urls
