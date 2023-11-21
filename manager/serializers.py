from rest_framework import serializers

from core.models import Manager, BillingHistory, TableNo


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = "__all__"


class ManagerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ["username", "password", "is_removed"]


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
