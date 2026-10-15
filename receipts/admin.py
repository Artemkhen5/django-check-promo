from django.contrib import admin

from receipts.models import Receipt


# Register your models here.
@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "fn",
        "fd",
        "fp",
        "purchase_date",
        "amount",
        "status",
        "user",
        "created_at",
    )
    list_filter = ("status", "purchase_date")
    search_fields = ("fn", "fd", "fp", "user__username")

    readonly_fields = (
        "fn",
        "fd",
        "fp",
        "purchase_date",
        "purchase_time",
        "amount",
        "user",
        "created_at",
    )