from django.urls import path

from receipts.views import ReceiptListView, ReceiptCreateView

urlpatterns = [
    path('', ReceiptListView.as_view(), name='receipt-list'),
    path('new/', ReceiptCreateView.as_view(), name='receipt-create'),
]