from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.enums import OrderStatus, PaymentStatus
from core.models import Universal, Menu, TableNo, RestaurantTable, Item, Tax, Order, UserOrderHistory
from common.permissions import IsAdminOrReadOnly
from customer.serializers import MenuSerializer, UniversalSerializer, OrderSerializer, OrderItemsSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UniversalSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Universal.objects.filter(is_removed=False)

    @action(detail=False, methods=['GET'], url_path='add_manager')
    def add_manager(self, request, *args, **kwargs):
        from manager.serializers import ManagerSerializer
        serializer = ManagerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Manager added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Invalid payload format"}, status=status.HTTP_400_BAD_REQUEST)


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
        items = [Item(item_id=item.id, order_id=order_obj.id, quantity=order_obj.quantity) for item in items]
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
