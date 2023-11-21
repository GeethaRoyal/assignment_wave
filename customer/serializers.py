from rest_framework import serializers

from core.models import Menu, Universal, Order
from core.serializers import ItemSerializer


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"


class UniversalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Universal
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderItemsSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "total", "items"]
