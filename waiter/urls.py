from django.urls import path, include
from rest_framework.routers import DefaultRouter
from waiter.views import OrderViewSet, WaiterHistoryViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'waiter-history', WaiterHistoryViewSet, basename='waiter-history')
router.register(r'order', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
