"""Модуль содержащий нотацию для настроек админ-панели"""
from django.contrib import admin

from user.models import User, Project, Employee


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс настроек админ-панели пользователя"""


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Класс настроек админ-панели проекта"""


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Класс настроек админ-панели сотрудника"""
