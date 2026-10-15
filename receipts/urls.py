from django.urls import path

from receipts.views import ReceiptListView

urlpatterns = [
    path('', ReceiptListView.as_view(), name='receipt-list'),
]