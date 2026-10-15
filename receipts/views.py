from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from receipts.forms import ReceiptForm
from receipts.models import Receipt


# Create your views here.
class ReceiptListView(LoginRequiredMixin, ListView):
    model = Receipt
    template_name = 'receipts/receipt_list.html'
    context_object_name = 'receipts'
    paginate_by = 10

    def get_queryset(self):
        return Receipt.objects.filter(user=self.request.user)


class ReceiptCreateView(LoginRequiredMixin, CreateView):
    form_class = ReceiptForm
    template_name = "receipts/receipt_form.html"
    success_url = reverse_lazy("receipt-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
