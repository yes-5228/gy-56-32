from django.db import models


class Attraction(models.Model):
    CATEGORY_CHOICES = [
        ("nature", "自然风光"),
        ("culture", "人文历史"),
        ("family", "亲子休闲"),
        ("food", "美食街区"),
    ]

    name = models.CharField("景点名称", max_length=80)
    city = models.CharField("城市", max_length=50)
    category = models.CharField("类型", max_length=20, choices=CATEGORY_CHOICES)
    duration_hours = models.DecimalField("建议游玩小时", max_digits=4, decimal_places=1)
    ticket_price = models.DecimalField("门票价格", max_digits=8, decimal_places=2, default=0)
    highlight = models.CharField("亮点", max_length=160)
    sort_order = models.PositiveIntegerField("排序", default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name
