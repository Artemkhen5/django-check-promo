from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if context["is_paginated"]:
            context["page_range"] = context["paginator"].get_elided_page_range(
                number=context["page_obj"].number,
                on_each_side=1,
                on_ends=1,
            )

        return context


class ReceiptCreateView(LoginRequiredMixin, CreateView):
    form_class = ReceiptForm
    template_name = "receipts/receipt_form.html"
    success_url = reverse_lazy("receipt-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["promo_start_date"] = settings.PROMO_START_DATE
        context["promo_end_date"] = settings.PROMO_END_DATE
        return context

    def expects_json(self):
        return "application/json" in self.request.headers.get("Accept", "")

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        if self.expects_json():
            return JsonResponse(
                {
                    "message": "Чек отправлен на проверку.",
                    "redirect_url": self.get_success_url(),
                },
                status=201,
            )

        return response

    def form_invalid(self, form):
        if self.expects_json():
            errors = {
                field: [str(error) for error in field_errors]
                for field, field_errors in form.errors.items()
            }
            return JsonResponse({"errors": errors}, status=400)

        return super().form_invalid(form)
