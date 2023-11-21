from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.enums import OrderStatus, UserRoles
from core.models import Order, WaiterHistory, RestaurantWaiter
from common.permissions import OrderPermission, IsWaiterOrManager
from core.serializers import WaiterHistorySerializer
from customer.serializers import UniversalSerializer, OrderSerializer


# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = OrderPermission

    @action(detail=False, methods=['GET'], url_path='waiter_unaccepted_order')
    def show_waiter_unaccepted_order(self, request):
        unaccepted_orders = self.queryset.filter(status=OrderStatus.PENDING.value, payment_status='pending')
        serializer = self.serializer_class(unaccepted_orders, many=True)
        return Response({'result': serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='accept_order')
    def accept_order(self, request):
        order_id = request.data.get('order_id')
        try:
            order = self.queryset.get(order_id=order_id, status='pending', payment_status='pending')
            order.status = OrderStatus.ACCEPTED.value
            order.save()
            serializer = self.serializer_class(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found or already accepted'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['POST'], url_path='decline_order')
    def decline_order(self, request):
        order_id = request.data.get('order_id')
        try:
            order = self.queryset.get(order_id=order_id, status='pending', payment_status='pending')
            order.status = OrderStatus.REJECTED.value
            order.save()
            serializer = self.serializer_class(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found or already declined'}, status=status.HTTP_404_NOT_FOUND)


class WaiterHistoryViewSet(viewsets.ModelViewSet):
    queryset = WaiterHistory.objects.filter(is_removed=False)
    serializer_class = WaiterHistorySerializer
    permission_classes = [IsWaiterOrManager]

    @action(detail=False, methods=['POST'])
    def delete_waiter_manager(self, request):
        waiter_id = request.data.get('waiter_id')
        waiter_obj = get_object_or_404(RestaurantWaiter, waiter_id)
        waiter_obj.delete()
        return Response({"message": "Removed"})

    @action(detail=False, methods=['POST'])
    def set_waiter(self, request):
        return Response({"message": "done"})

    @action(detail=False, methods=['GET'])
    def get_waiter(self, request):
        queryset_waiters = RestaurantWaiter.objects.filter(role=UserRoles.WAITER.value, is_removed=False)
        serializer = UniversalSerializer(queryset_waiters, many=True)
        return Response(serializer.data)
