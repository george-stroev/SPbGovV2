"""Модуль, сохраняющий классы прав доступа к viewers"""
from rest_framework.permissions import BasePermission


class IsYourEmployeePermission(BasePermission):
    """
    Доступ будет разрешен, только если ты
    владеешь проектом, к которому
    относится сотрудник
    """
    def has_object_permission(self, request, view, obj):
        """
        Верните "True", если разрешение получено, или "False" в противном случае.
        """
        return obj.project.user.id == request.user.id


class IsYourProjectPermission(BasePermission):
    """
    Доступ будет разрешен, только если ты
    владеешь проектом
    """

    def has_object_permission(self, request, view, obj):
        """
        Верните "True", если разрешение получено, или "False" в противном случае.
        """
        return obj.user.id == request.user.id
