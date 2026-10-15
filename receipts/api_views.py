from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from receipts.models import Receipt
from receipts.serializers import ReceiptSerializer


class ReceiptListAPIView(ListAPIView):
    serializer_class = ReceiptSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Receipt.objects.filter(user=self.request.user)
