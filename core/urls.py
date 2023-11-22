from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (
    CheckUsernameAPIView, AdminUsersViewSet, DJViewSet
)
from manager.views import BillingHistoryViewSet, TableNoViewSet, ManagerViewSet, WaiterHistoryViewSet, OrderViewSet, \
    MenuViewSet
from customer.views import UserViewSet, UserOrderViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'waiter-history', WaiterHistoryViewSet, basename='waiter-history')
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'table-no', TableNoViewSet, basename='table-no')
router.register(r'billing-history', BillingHistoryViewSet, basename='billing-history')
router.register(r'admin', AdminUsersViewSet, basename='admin-view')
router.register(r'order', OrderViewSet, basename='order')
router.register(r'user-order', UserOrderViewSet, basename='user-order')
router.register(r'user', UserViewSet, basename="users")
router.register(r'dj', DJViewSet, basename='dj')


urlpatterns = [
    path('', include(router.urls)),
]
