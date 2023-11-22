from django.urls import path, include
from rest_framework.routers import DefaultRouter
from manager.views import BillingHistoryViewSet, TableNoViewSet, ManagerViewSet, WaiterHistoryViewSet, OrderViewSet
from customer.views import UserViewSet, UserOrderViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'user-order', UserOrderViewSet, basename='user-order')
router.register(r'user', UserViewSet, basename="users")

urlpatterns = [
    path('', include(router.urls)),

]
