from rest_framework import serializers

from receipts.models import Receipt


class ReceiptSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Receipt
        fields = (
            "id",
            "fn",
            "fd",
            "fp",
            "purchase_date",
            "purchase_time",
            "amount",
            "status",
            "status_display",
            "rejection_reason",
            "created_at",
        )
        read_only_fields = fields
