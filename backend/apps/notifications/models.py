from django.db import models

from apps.routes.models import TravelRoute


class TravelNotice(models.Model):
    TYPE_CHOICES = [
        ("assembly", "集合提醒"),
        ("weather", "天气提示"),
        ("packing", "物品清单"),
        ("change", "行程变更"),
    ]

    route = models.ForeignKey(TravelRoute, related_name="notices", on_delete=models.CASCADE)
    notice_type = models.CharField("通知类型", max_length=20, choices=TYPE_CHOICES)
    title = models.CharField("标题", max_length=100)
    content = models.TextField("内容")
    publish_at = models.DateTimeField("发布时间")
    is_sent = models.BooleanField("已发送", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-publish_at", "id"]

    def __str__(self):
        return self.title
