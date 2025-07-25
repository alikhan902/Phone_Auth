from rest_framework.permissions import BasePermission

class IsNotAuthenticated(BasePermission):
    """
    Доступ только для неавторизованных пользователей.
    """
    def has_permission(self, request, view):
        return not request.user or not request.user.is_authenticated