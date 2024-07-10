"""Модуль настроек приложения user"""
from django.apps import AppConfig


class UserConfig(AppConfig):
    """Класс настроек приложения user"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
