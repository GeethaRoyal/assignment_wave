# permissions.py
from rest_framework import permissions

from common.enums import UserRoles


class IsManager(permissions.BasePermission):
    """
    Custom permission to only allow managers to access the view.
    """

    def has_permission(self, request, view):
        # Assuming 'role' is a field in your Manager model indicating the user role
        return request.user and request.user.role == UserRoles.MANAGER.value


class IsWaiterOrManager(permissions.BasePermission):
    """
    Custom permission to only allow waiters or managers to access the view.
    """

    def has_permission(self, request, view):
        # Assuming 'role' is a field in your Manager model indicating the user role
        return request.user and (
                request.user.role == UserRoles.MANAGER.value or request.user.role == UserRoles.WAITER.value)


class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow managers full access, but only read access for others.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Assuming 'role' is a field in your Manager model indicating the user role
        return request.user and request.user.role == UserRoles.MANAGER.value


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow owners of an object to edit it, but read-only for others.
    """

    def has_object_permission(self, request, view, obj):
        # Assuming 'user' is a field in your models representing the user associated with an object
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow read-only access for everyone
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Check if the user has core role
        return request.user and request.user.role == UserRoles.ADMIN.value


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user has customer role
        return request.user and request.user.role == UserRoles.CUSTOMER.value


class OrderPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = request.user.role
        if user_role == UserRoles.ADMIN.value:
            return True
        if user_role == UserRoles.MANAGER.value:
            if view.action in ["waiter_unaccepted_order"]:
                return True
        if user_role == UserRoles.WAITER.value:
            if view.action in ["accept_order", "reject_order"]:
                return True

        else:
            return False
