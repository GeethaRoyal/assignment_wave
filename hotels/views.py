from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from hotels.enums import BillingStatus, PaymentStatus, UserRoles, OrderStatus
from hotels.models import (
    Manager,
    UserOrderHistory,
    WaiterHistory,
    Menu,
    BillingHistory,
    TableNo, RestaurantWaiter, Order, RestaurantTable, Universal, Item, Tax, Allotment, DJ,
)
from hotels.serializers import (
    ManagerSerializer,
    WaiterHistorySerializer,
    MenuSerializer,
    BillingHistorySerializer,
    TableNoSerializer, TableNoListSerializer, RestaurantWaiterSerializer, AdminViewCountSerializer, OrderSerializer,
    UniversalSerializer, OrderItemsSerializer, DJSerializer,
)
from hotels.permissions import IsManager, IsWaiterOrManager, IsManagerOrReadOnly, IsAdminOrReadOnly, OrderPermission


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.filter(is_removed=False)
    serializer_class = ManagerSerializer
    permission_classes = [IsManager, IsAdminOrReadOnly]


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


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.filter(is_removed=False)
    serializer_class = MenuSerializer
    permission_classes = [IsManagerOrReadOnly]

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


class CheckUsernameAPIView(APIView):
    permission_required = IsAuthenticated
    serializer_class = UniversalSerializer

    def post(self, request,username, password):
        try:
            user_obj = Universal.objects.filter(username=username, passowrd=password)
            return Response(user_obj[0])
        except Universal.DoesNotExist as e:
            return Response({'message': "User Not found"}, status=status.HTTP_404_NOT_FOUND)


class AdminUsersViewSet(viewsets.GenericViewSet):
    queryset_managers = Universal.objects.filter(role=UserRoles.MANAGER.value)
    queryset_users = Universal.objects.filter(role=UserRoles.CUSTOMER.value)
    queryset_waiters = Universal.objects.filter(role=UserRoles.WAITER.value)
    serializer_class_managers = ManagerSerializer
    serializer_class_users = RestaurantWaiterSerializer
    serializer_class_count = AdminViewCountSerializer
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get_serializer_class(self):
        if self.action == 'manager_list':
            return self.serializer_class_managers
        elif self.action == 'users_list':
            return self.serializer_class_users
        elif self.action == 'remove_manager':
            return ""
        else:
            return self.serializer_class_count

    @action(detail=False, methods=['GET'], url_path='manager_list')
    def admin_manager_list(self, request):
        managers = self.queryset_managers
        serializer = self.serializer_class_managers(managers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='users_list')
    def admin_user_list(self, request):
        users = self.queryset_users
        serializer = self.serializer_class_users(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='count_manager')
    def admin_count_manager(self, request):
        count = self.queryset_managers.count()
        return Response({"count": count})

    @action(detail=False, methods=['GET'], url_path='count_waiter')
    def admin_count_waiter(self, request):
        count = self.queryset_waiters.count()
        return Response({"count": count})

    @action(detail=False, methods=['GET'], url_path='count_orders')
    def admin_count_orders(self, request, *args, **kwargs):
        count = Order.objects.count()
        return Response({"count": count})

    @action(detail=False, methods=['POST'], url_path='remove_manager')
    def admin_remove_manager(self, request):
        manager_id = request.data.get('id')
        try:
            manager = self.queryset_managers.get(id=manager_id)
            manager.is_removed = True
            manager.save()
            return Response({'message': 'Manager removed successfully'})
        except Manager.DoesNotExist:
            return Response({'message': 'Manager not found'}, status=404)

    @action(detail=False, methods=['POST'], url_path='remove_user')
    def admin_remove_user(self, request):
        user_id = request.data.get('id')
        try:
            user = self.queryset_waiters.get(id=user_id)
            user.is_removed = True
            user.save()
            return Response({'message': 'User removed successfully'})
        except RestaurantWaiter.DoesNotExist:
            return Response({'message': 'User not found'}, status=404)


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


## Customer APIs

class UserOrderViewSet(viewsets.ViewSet):
    def list(self, request, table_id, restaurant_id):
        menus = Menu.objects.filter(restaurant_id=restaurant_id)
        serializer = MenuSerializer(menus, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], url_path='create_order')
    def create_order(self, request, table_id, restaurant_id):
        # validate if table_id, menu exists
        data = request.data
        user = request.user
        menu_id = data["menu_id"]
        category_id = data["category_id"]
        quantity = data["quantity"]
        items = data["items"]
        item_ids = [item.id for item in items]
        get_object_or_404(TableNo, table_id)
        get_object_or_404(Menu, menu_id)
        item_id_price_map = {item.id: item.quantity for item in items}
        restaurant_table = RestaurantTable.objects.filter(table_id=table_id, restaurant_id=restaurant_id)
        if not restaurant_table:
            return Response({'message': 'Table not found in restaurant'}, status=status.HTTP_404_NOT_FOUND)
        items_price = Item.objects.filter(menu__category_id=category_id, menu_id=menu_id, id__in=item_ids)
        total_price = sum(item_price * item_id_price_map[item_price.id] for item_price in items_price)
        tax = Tax.objects.get(restaurant_id=restaurant_id, is_removed=False)
        if tax:
            total_price = total_price + ((total_price / tax.tax) * 100) + ((total_price / tax.GST) * 100) + (
                    (total_price / tax.offer) * 100)
        order_obj = Order(
            table_no=table_id,
            restaurant_id=restaurant_id,
            menu_id=menu_id,
            category_id=category_id,
            total=total_price,
            user_id=user.id,
            status=OrderStatus.PENDING.value,
            payment_status=PaymentStatus.UNPAID.value,
            date_time=datetime.now()
        )
        order_obj.save()
        items = [Item(item_id=item.id, order_id=order_obj.id, quantity=order_obj.quantity )for item in items]
        Item.bulk_create(items)

        # create UserOrderHistory
        user_order_history = UserOrderHistory(
            order_id=order_obj.id,
            quantity=quantity,
            customer_id=user.id,
            menu_id=menu_id
        )
        user_order_history.save()
        return Response({'message': 'Order created successfully'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'], url_path='order_history')
    def order_history(self, request, table_id, restaurant_id):
        orders = Order.objects.filter(table_id=table_id, restaurant_id=restaurant_id).prefetch_related("items")
        serializer = OrderItemsSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"], url_path="take_order")
    def take_order(self, request, *args, **kwargs):
        try:
            serializer = OrderSerializer(data=request.data)

            if serializer.is_valid():
                # Save the order
                serializer.save()

                return Response({"message": "Order received successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UniversalSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Universal.objects.filter(is_removed=False)

    @action(detail=False, methods=['GET'], url_path='add_manager')
    def add_manager(self, request, *args, **kwargs):
        serializer = ManagerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Manager added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Invalid payload format"}, status=status.HTTP_400_BAD_REQUEST)


class DJViewSet(viewsets.ModelViewSet):
    serializer_class = DJSerializer
    permission_classes = [IsAuthenticated]
    queryset = DJ.objects.filter(is_removed=False)
