# serializers.py
from rest_framework import serializers
from .models import UserOrderHistory, WaiterHistory, RestaurantWaiter, Item, DJ


class UserOrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOrderHistory
        fields = "__all__"


class WaiterHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WaiterHistory
        fields = "__all__"


class RestaurantWaiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantWaiter
        fields = "__all__"



class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "type", "price", "category_name"]


class DJSerializer(serializers.ModelSerializer):
    class Meta:
        model = DJ
        fields = "__all__"