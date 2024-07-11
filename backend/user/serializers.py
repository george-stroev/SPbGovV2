"""Модуль, содержащий классы сериализации моделей"""
from rest_framework import serializers

from user.models import Employee, User, Project


class EmployeeSerializer(serializers.ModelSerializer):
    """Сериализатор сотрудника"""
    # pylint: disable=C0115
    class Meta:
        model = Employee
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    """Сериализатор проекта"""
    # pylint: disable=C0115
    class Meta:
        model = Project
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    # pylint: disable=C0115
    class Meta:
        model = User
        fields = ["username", "password"]
