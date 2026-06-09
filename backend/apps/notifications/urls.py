from rest_framework.routers import DefaultRouter

from .views import TravelNoticeViewSet

router = DefaultRouter()
router.register("", TravelNoticeViewSet, basename="travel-notice")

urlpatterns = router.urls
