from rest_framework import serializers

from core.models import BillingHistory, Order
from core.serializers import ItemSerializer


class OrderItemsSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "total", "items"]


class BillingHistorySerializer(serializers.ModelSerializer):
    order = OrderItemsSerializer()

    class Meta:
        model = BillingHistory
        fields = ["order", "id", "transaction_id", "table", "payment_status", "waiter_id"]
