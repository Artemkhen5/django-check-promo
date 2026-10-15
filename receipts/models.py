from django.conf import settings
from django.db import models


# Create your models here.
class Receipt(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "На проверке"
        APPROVED = "approved", "Принят"
        REJECTED = "rejected", "Отклонен"

    fn = models.CharField("ФН", max_length=64)
    fd = models.CharField("ФД", max_length=64)
    fp = models.CharField("ФП", max_length=64)

    purchase_date = models.DateField("Дата покупки")
    purchase_time = models.TimeField("Время покупки")
    amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2)

    status = models.CharField(
        "Статус",
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    rejection_reason = models.TextField("Причина отказа", blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="receipts",
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        verbose_name = "Чек"
        verbose_name_plural = "Чеки"
        constraints = [
            models.UniqueConstraint(
                fields=["fn", "fd", "fp"],
                name="unique_receipt_fiscal_data"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Чек {self.fn}/{self.fd}"
