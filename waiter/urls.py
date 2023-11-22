from django.urls import path, include
from rest_framework.routers import DefaultRouter

from waiter.views import PaymentStatusViewSet, BillViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'payment', PaymentStatusViewSet, basename='payment')
router.register(r'bill', BillViewSet, basename='bill')

urlpatterns = [
    path('', include(router.urls)),
]
