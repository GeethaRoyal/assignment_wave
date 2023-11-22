# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from common.constants import PAYMENT_STATUS_CHOICES
from common.permissions import IsWaiter
from core.models import Order, BillingHistory
from waiter.serializers import BillingHistorySerializer


class PaymentStatusViewSet(viewsets.ViewSet):
    permission_classes = [IsWaiter]

    def post(self, request, order_id):
        payment_status = request["payment_status"]
        order_obj = get_object_or_404(Order, order_id)
        if payment_status not in PAYMENT_STATUS_CHOICES:
            return Response({"message": "invalid payment status choice"}, status=status.HTTP_404_NOT_FOUND)
        order_obj.payment_status = payment_status
        order_obj.save()
        return Response({"message": "payment status updated successfully"}, status=status.HTTP_200_OK)


class BillViewSet(viewsets.ViewSet):
    permission_classes = [IsWaiter]

    def get(self, request, order_id, restaurant_id):
        bill_obj = BillingHistory.objects.filter(order_id=order_id, restaurant_id=restaurant_id).select_related("order")
        if not bill_obj:
            return Response({"message": "Bill Doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BillingHistorySerializer(bill_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


