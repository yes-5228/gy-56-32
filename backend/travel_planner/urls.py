from django.contrib import admin
from django.db import connection
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health_check(request):
    checks = {}
    all_ok = True

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
        all_ok = False

    if checks.get("database") == "ok":
        try:
            tables = connection.introspection.table_names()
            required = [
                "attractions_attraction",
                "routes_travelroute",
                "routes_routestop",
                "bookings_booking",
                "notifications_travelnotice",
            ]
            missing = [t for t in required if t not in tables]
            if missing:
                checks["migrations"] = f"missing tables: {', '.join(missing)}"
                all_ok = False
            else:
                checks["migrations"] = "ok"
        except Exception as e:
            checks["migrations"] = f"error: {e}"
            all_ok = False
    else:
        checks["migrations"] = "skipped"

    if checks.get("migrations") == "ok":
        try:
            from apps.attractions.models import Attraction
            from apps.routes.models import TravelRoute

            attraction_count = Attraction.objects.count()
            route_count = TravelRoute.objects.count()
            if attraction_count > 0 and route_count > 0:
                checks["demo_data"] = "ok"
            else:
                checks["demo_data"] = (
                    f"incomplete: attractions={attraction_count}, routes={route_count}"
                )
                all_ok = False
        except Exception as e:
            checks["demo_data"] = f"error: {e}"
            all_ok = False
    else:
        checks["demo_data"] = "skipped"

    status_code = 200 if all_ok else 503
    return Response(
        {
            "status": "ok" if all_ok else "unhealthy",
            "service": "travel-planner",
            "checks": checks,
        },
        status=status_code,
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check),
    path("api/attractions/", include("apps.attractions.urls")),
    path("api/routes/", include("apps.routes.urls")),
    path("api/bookings/", include("apps.bookings.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
]
