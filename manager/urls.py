from django.urls import path, include
from rest_framework.routers import DefaultRouter
from manager.views import BillingHistoryViewSet, TableNoViewSet, ManagerViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'table-no', TableNoViewSet, basename='table-no')
router.register(r'billing-history', BillingHistoryViewSet, basename='billing-history')

urlpatterns = [
    path('', include(router.urls))
]
