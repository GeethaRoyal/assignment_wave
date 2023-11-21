from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (
    MenuViewSet,
    CheckUsernameAPIView, AdminUsersViewSet, DJViewSet
)
from manager.views import BillingHistoryViewSet, TableNoViewSet, ManagerViewSet
from waiter.views import OrderViewSet, WaiterHistoryViewSet
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
schema_view = get_schema_view(
    openapi.Info(
        title="Song Wave",
        default_version='v1',
        description="Your API description",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path('check_username/', CheckUsernameAPIView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
