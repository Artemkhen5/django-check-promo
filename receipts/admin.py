from django.contrib import admin

from receipts.models import Receipt
from django import forms


# Register your models here.
class ReceiptAdminForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        reason = cleaned_data.get("rejection_reason")

        if status == Receipt.Status.REJECTED and not (reason or "").strip():
            self.add_error(
                "rejection_reason",
                "Укажите причину отклонения чека"
            )

        return cleaned_data


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    form = ReceiptAdminForm
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
