# serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Manager, UserOrderHistory, WaiterHistory, Menu, BillingHistory, TableNo, RestaurantWaiter, Order, \
    Universal, Item, DJ


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = "__all__"


class ManagerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ["username", "password", "is_removed"]


class UserOrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOrderHistory
        fields = "__all__"


class WaiterHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WaiterHistory
        fields = "__all__"


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"


class BillingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingHistory
        fields = "__all__"


class TableNoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableNo
        fields = "__all__"


class TableNoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableNo
        fields = ["table_no", "url"]


class RestaurantWaiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantWaiter
        fields = "__all__"


class UniversalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Universal
        fields = "__all__"


class AdminViewCountSerializer(serializers.ModelField):
    count = serializers.IntegerField()


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "type", "price", "category_name"]


class OrderItemsSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "total", "items"]

class DJSerializer(serializers.ModelSerializer):
    class Meta:
        model = DJ
        fields = "__all__"