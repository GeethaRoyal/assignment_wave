from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from common.enums import BillingStatus, PaymentStatus, UserRoles, OrderStatus
from core.models import BillingHistory, TableNo, Allotment, Manager, WaiterHistory, RestaurantWaiter, Order, Menu, Tax, \
    RestaurantTable
from common.permissions import IsManagerOrReadOnly, IsManager, IsAdminOrReadOnly, IsWaiterOrManager, OrderPermission
from core.serializers import WaiterHistorySerializer
from customer.serializers import UniversalSerializer, OrderSerializer, MenuSerializer, TaxSerializer, \
    AllotmentSerializer
from manager.serializers import ManagerSerializer, BillingHistorySerializer, TableNoSerializer, TableNoListSerializer


# Create your views here.

class BillingHistoryViewSet(viewsets.ModelViewSet):
    queryset = BillingHistory.objects.filter(is_removed=False)
    serializer_class = BillingHistorySerializer
    permission_classes = [IsManagerOrReadOnly]

    def list(self, request, *args, **kwargs):
        paginator = CustomPagination()
        tables = BillingHistory.objects.all()
        result_page = paginator.paginate_queryset(tables, request)
        serializer = BillingHistorySerializer(result_page, many=True)

        response_data = {
            'billing_history': serializer.data,
            'pagination': {
                'total_pages': paginator.page.paginator.num_pages,
                'current_page': paginator.page.number,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
            }
        }

        return Response(response_data)

    @action(detail=False, methods=['GET'], url_path="live")
    def live_billing_history(self, request):
        payload = BillingHistory.objects.filter(
            status=BillingStatus.PENDING.value, payment_status=PaymentStatus.UNPAID.value)
        return Response({"payload": payload})


class TableNoViewSet(viewsets.ModelViewSet):
    queryset = TableNo.objects.filter(is_removed=False)
    serializer_class = TableNoListSerializer
    permission_classes = [IsManagerOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = TableNoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Done"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def remove_table(self, request):
        table_no = request.data.get('table_no', None)
        if not table_no:
            return Response({"message": "Table number parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            table_obj = (TableNo.objects.filter(table_no=table_no, is_removed=False))
            restaurant_id = table_obj.restaurant_id
            table_obj.delete()
            Allotment.objects.filter(table_no=table_no, restaurant_id=restaurant_id).delete()
            return Response({"message": "Done"})
        except TableNo.DoesNotExist:
            return Response({"message": "Table not found"}, status=status.HTTP_404_NOT_FOUND)


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.filter(is_removed=False)
    serializer_class = ManagerSerializer
    permission_classes = [IsManager, IsAdminOrReadOnly]


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


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


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.filter(is_removed=False)
    serializer_class = MenuSerializer
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        menu_items = Menu.objects.filter(is_removed=False)
        serializer = MenuSerializer(menu_items, many=True)

        return Response({"menu": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = MenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Menu item added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        menu_name = request.data.get('name', None)
        if not menu_name:
            return Response({"message": "Name parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            menu_item = Menu.objects.get(menu_name=menu_name)
            menu_item.is_removed = True
            menu_item.save()
            return Response({"message": "Done"})
        except Menu.DoesNotExist:
            return Response({"message": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)


class TaxViewSet(viewsets.ModelViewSet):
    queryset = Tax.objects.filter(is_removed=False)
    serializer_class = TaxSerializer
    permission_classes = [IsManager, IsAdminOrReadOnly]


class AllotmentViewSet(viewsets.ModelViewSet):
    queryset = Allotment.objects.filter(is_removed=False)
    serializer_class = AllotmentSerializer
    permission_classes = [IsManager, IsAdminOrReadOnly]

    @action(detail=False, methods=['POST'])
    def allotment_status(self, request, table_id, restaurant_id):
        get_object_or_404(TableNo, table_id)
        restaurant_table = RestaurantTable.objects.filter(table_id=table_id, restaurant_id=restaurant_id)
        if not restaurant_table:
            return Response({"message": "Table not found Restaurant"}, status=status.HTTP_404_NOT_FOUND)
        allotment_status = Allotment.objects.filter(restaurant_id=restaurant_id, table_id=table_id, reserved_status=1)
        if allotment_status:
            return Response({"message": "Table is Already Reserved"}, status=status.HTTP_200_OK)
        return Response({"message": "Table is not Reserved"}, status=status.HTTP_200_OK)
