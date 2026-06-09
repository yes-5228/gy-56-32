from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.attractions.models import Attraction
from apps.bookings.models import Booking
from apps.notifications.models import TravelNotice
from apps.routes.models import RouteStop, TravelRoute


class Command(BaseCommand):
    help = "Create demo data for the travel planning system."

    def handle(self, *args, **options):
        attractions = [
            {
                "name": "西湖苏堤",
                "city": "杭州",
                "category": "nature",
                "duration_hours": Decimal("2.5"),
                "ticket_price": Decimal("0"),
                "highlight": "湖景步道与经典城市风光",
                "sort_order": 1,
            },
            {
                "name": "灵隐寺",
                "city": "杭州",
                "category": "culture",
                "duration_hours": Decimal("2.0"),
                "ticket_price": Decimal("75"),
                "highlight": "古刹、飞来峰造像与祈福体验",
                "sort_order": 2,
            },
            {
                "name": "宋城景区",
                "city": "杭州",
                "category": "family",
                "duration_hours": Decimal("3.5"),
                "ticket_price": Decimal("320"),
                "highlight": "沉浸式演艺和亲子项目",
                "sort_order": 3,
            },
            {
                "name": "夫子庙秦淮河",
                "city": "南京",
                "category": "culture",
                "duration_hours": Decimal("3.0"),
                "ticket_price": Decimal("80"),
                "highlight": "夜游秦淮与明清街区",
                "sort_order": 4,
            },
        ]

        created_attractions = {}
        for data in attractions:
            attraction, _ = Attraction.objects.update_or_create(
                name=data["name"],
                defaults=data,
            )
            created_attractions[data["name"]] = attraction

        route, _ = TravelRoute.objects.update_or_create(
            title="杭州湖山文化 2 日游",
            defaults={
                "city": "杭州",
                "days": 2,
                "transport": "高铁往返 + 市内巴士",
                "hotel_level": "舒适型四星酒店",
                "min_group_size": 6,
                "max_group_size": 18,
                "base_cost": Decimal("980"),
                "guide_fee": Decimal("120"),
                "status": "forming",
                "description": "串联西湖、灵隐寺与宋城演艺，适合家庭和轻度文化游。",
            },
        )
        route.stops.all().delete()
        for stop in [
            ("西湖苏堤", 1, 1, "上午慢行苏堤，预留拍照和茶歇时间"),
            ("灵隐寺", 1, 2, "下午参观飞来峰与寺院建筑"),
            ("宋城景区", 2, 1, "午后入园，晚间观看大型演出"),
        ]:
            RouteStop.objects.create(
                route=route,
                attraction=created_attractions[stop[0]],
                day=stop[1],
                order=stop[2],
                note=stop[3],
            )

        Booking.objects.update_or_create(
            route=route,
            phone="13800000001",
            defaults={
                "contact_name": "李女士",
                "party_size": 3,
                "travel_date": date.today() + timedelta(days=14),
                "status": "confirmed",
                "remark": "需要安排亲子房",
            },
        )
        Booking.objects.update_or_create(
            route=route,
            phone="13800000002",
            defaults={
                "contact_name": "王先生",
                "party_size": 2,
                "travel_date": date.today() + timedelta(days=14),
                "status": "pending",
                "remark": "素食餐",
            },
        )

        TravelNotice.objects.update_or_create(
            route=route,
            title="杭州湖山文化 2 日游集合通知",
            defaults={
                "notice_type": "assembly",
                "content": "请于出行日 08:30 前到达杭州东站东广场集合，携带身份证件。",
                "publish_at": timezone.now(),
                "is_sent": True,
            },
        )
        TravelNotice.objects.update_or_create(
            route=route,
            title="雨具与轻便鞋提醒",
            defaults={
                "notice_type": "packing",
                "content": "西湖步行时间较长，请准备轻便鞋；若遇阵雨建议携带折叠伞。",
                "publish_at": timezone.now() + timedelta(hours=2),
                "is_sent": False,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
