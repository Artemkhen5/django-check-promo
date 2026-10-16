from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from receipts.forms import ReceiptForm
from receipts.models import Receipt


# Create your tests here.
@override_settings(
    PROMO_START_DATE=date(2026, 10, 1),
    PROMO_END_DATE=date(2026, 10, 31)
)
class ReceiptFormTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            username="test-user ",
            password="test-password-123"
        )
        self.valid_data = {
            "fn": "1234567890",
            "fd": "98765",
            "fp": "1122334455",
            "purchase_date": "2026-10-15",
            "purchase_time": "12:30",
            "amount": "1500.00"
        }

    def test_date_inside_promo_period_is_valid(self):
        form = ReceiptForm(data=self.valid_data)

        self.assertTrue(form.is_valid(), form.errors)

    def test_promo_period_start_and_end_dates_are_valid(self):
        for purchase_date in ("2026-10-01", "2026-10-31"):
            data = {**self.valid_data, "purchase_date": purchase_date}
            form = ReceiptForm(data=data)

            with self.subTest(purchase_date=purchase_date):
                self.assertTrue(form.is_valid(), form.errors)

    def test_dates_outside_promo_period_are_invalid(self):
        for purchase_date in ("2026-09-30", "2026-11-01"):
            data = {**self.valid_data, "purchase_date": purchase_date}
            form = ReceiptForm(data=data)

            with self.subTest(purchase_date=purchase_date):
                self.assertFalse(form.is_valid(), form.errors)
                self.assertIn("purchase_date", form.errors)

    def test_minimum_amount_is_valid(self):
        data = {**self.valid_data, "amount": "1000.00"}
        form = ReceiptForm(data=data)

        self.assertTrue(form.is_valid(), form.errors)

    def test_amount_bellow_minimum_value_is_invalid(self):
        data = {**self.valid_data, "amount": "999.99"}
        form = ReceiptForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_duplicate_fiscal_data_is_rejected(self):
        Receipt.objects.create(
            fn=self.valid_data["fn"],
            fd=self.valid_data["fd"],
            fp=self.valid_data["fp"],
            purchase_date=date(2026, 10, 15),
            purchase_time="12:30",
            amount=Decimal("1500.00"),
            user=self.user
        )

        form = ReceiptForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.non_field_errors())

    def test_changing_one_fiscal_value_is_allowed(self):
        Receipt.objects.create(
            fn=self.valid_data["fn"],
            fd=self.valid_data["fd"],
            fp=self.valid_data["fp"],
            purchase_date=date(2026, 10, 15),
            purchase_time="12:30",
            amount=Decimal("1500.00"),
            user=self.user,
        )
        data = {**self.valid_data, "fp": "different-fp"}

        form = ReceiptForm(data=data)

        self.assertTrue(form.is_valid(), form.errors)

    def test_submitting_duplicate_shows_form_error_not_server_error(self):
        self.client.force_login(self.user)
        Receipt.objects.create(
            fn=self.valid_data["fn"],
            fd=self.valid_data["fd"],
            fp=self.valid_data["fp"],
            purchase_date=date(2026, 10, 15),
            purchase_time="12:30",
            amount=Decimal("1500.00"),
            user=self.user,
        )

        response = self.client.post(
            reverse("receipt-create"),
            self.valid_data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertEqual(
            Receipt.objects.filter(
                fn=self.valid_data["fn"],
                fd=self.valid_data["fd"],
                fp=self.valid_data["fp"],
            ).count(),
            1
        )

    def test_new_receipt_gets_pending_status(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("receipt-create"),
            self.valid_data,
        )

        self.assertEqual(response.status_code, 302)
        receipt = Receipt.objects.get(
            fn=self.valid_data["fn"],
            fd=self.valid_data["fd"],
            fp=self.valid_data["fp"],
        )
        self.assertEqual(receipt.status, Receipt.Status.PENDING)
