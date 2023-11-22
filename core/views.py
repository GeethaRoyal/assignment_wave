from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from common.enums import UserRoles
from core.models import (
    Manager,
    RestaurantWaiter, Order, Universal, DJ,
)
from core.serializers import (
    RestaurantWaiterSerializer, DJSerializer,
)
from customer.serializers import UniversalSerializer
from common.permissions import  IsAdminOrReadOnly


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
    serializer_class_managers = UniversalSerializer
    serializer_class_users = RestaurantWaiterSerializer
    # permission_classes = [IsAdminOrReadOnly, IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'manager_list':
            return self.serializer_class_managers
        elif self.action == 'users_list':
            return self.serializer_class_users

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

class DJViewSet(viewsets.ModelViewSet):
    serializer_class = DJSerializer
    permission_classes = [IsAuthenticated]
    queryset = DJ.objects.filter(is_removed=False)
