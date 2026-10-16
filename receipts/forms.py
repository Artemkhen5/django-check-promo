from decimal import Decimal

from django.conf import settings
from django import forms

from receipts.models import Receipt


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = (
            "fn",
            "fd",
            "fp",
            "purchase_date",
            "purchase_time",
            "amount",
        )
        widgets = {
            "fn": forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
            "fd": forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
            "fp": forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
            "purchase_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "purchase_time": forms.TimeInput(
                attrs={"type": "time"},
                format="%H:%M",
            ),
            "amount": forms.NumberInput(
                attrs={"min": "1000", "step": "0.01", "inputmode": "decimal"}
            ),
        }

    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if amount < Decimal("1000.00"):
            raise forms.ValidationError("Сумма покупки должна быть не меньше 1000 ₽.")

        return amount

    def clean_purchase_date(self):
        purchase_date = self.cleaned_data["purchase_date"]

        if not settings.PROMO_START_DATE <= purchase_date <= settings.PROMO_END_DATE:
            raise forms.ValidationError("Дата покупки не входит в период акции.")

        return purchase_date

    def clean(self):
        cleaned_data = super().clean()

        fn = cleaned_data.get("fn")
        fd = cleaned_data.get("fd")
        fp = cleaned_data.get("fp")

        if fn and fd and fp:
            duplicate_exists = Receipt.objects.filter(
                fn=fn,
                fd=fd,
                fp=fp,
            ).exists()

            if duplicate_exists:
                raise forms.ValidationError("Чек с такими ФН, ФД и ФП уже зарегистрирован.")

        return cleaned_data
