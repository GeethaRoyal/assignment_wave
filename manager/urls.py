from django.urls import path, include
from rest_framework.routers import DefaultRouter
from manager.views import BillingHistoryViewSet, TableNoViewSet, ManagerViewSet, TaxViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'managers', ManagerViewSet, basename='manager')
router.register(r'table-no', TableNoViewSet, basename='table-no')
router.register(r'billing-history', BillingHistoryViewSet, basename='billing-history')
router.register(r'tax', TaxViewSet, basename='taxes')

urlpatterns = [
    path('', include(router.urls))
]
