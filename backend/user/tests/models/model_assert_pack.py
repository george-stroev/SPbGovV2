"""
Модуль, содержащий вспомогательные при
тестировании моделей инструменты
"""
from functools import wraps
from typing import Any, Callable

from django.db import DataError, transaction, IntegrityError
from django.test import TestCase

from user.factories import ExplicitFactory
from user.models import ExplicitModel


def field_test_pack(field_name: str) -> Callable[[Callable], Any]:
    """
    Функция, создающая декоратор с аргументами

    Args:
         field_name: Имя тестируемого поля
    """
    def decorator(func: Callable) -> Callable:
        """
        Декоратор, подготавливающий тестируемый метод к тестам поля модели

        Args:
            func: Декорируемая функция
        """
        @wraps(func)
        def wrapper(self: TestCase, *args, **kwargs):
            """Функция, оборачивающая тест в subTest"""
            with self.subTest():
                return func(self, field_name=field_name, *args, **kwargs)

        return wrapper

    return decorator


# pylint: disable=missing-class-docstring
class BaseModelFieldsTestPack(TestCase):
    factory: type[ExplicitFactory]
    model: type[ExplicitModel]

    def assert_char_field_length(self, field_name: str, expected_max_length: int = 255):
        """
        Метод, тестирующий максимальную длину текстового поля

        Args:
            field_name: Имя тестируемого поля
            expected_max_length: Ожидаемая максимальная длина
        """
        self.assertEqual(
            self.model.objects.count(), 0,
            "Вероятно, что база данных не очищается между проверками",
        )
        long_field = "1" * (expected_max_length + 1)
        with self.assertRaises(DataError):
            with transaction.atomic():
                self.factory(**{field_name: long_field})
        self.assertEqual(
            self.model.objects.count(), 0,
            "Вероятно, что объект все равно попал в базу данных",
        )

        short_field = "1" * expected_max_length
        obj = self.factory(**{field_name: short_field})
        self.assertEqual(
            self.model.objects.count(), 1,
            "Вероятно, что запись объекта прошла не успешно",
        )

        obj.delete()
        self.assertEqual(
            self.model.objects.count(), 0,
            "Вероятно, что удаление объекта прошло не успешно",
        )

    def assert_unique_value(self, field_name: str, non_unique_value: Any = "non_unique_value"):
        """
        Метод, тестирующий уникальность поля

        Args:
            field_name: Имя тестируемого поля
            non_unique_value: Значение, которое будет подставляться в поле в процессе тестирования
        """
        self.assertEqual(
            self.model.objects.count(), 0,
            "Вероятно, что база данных не очищается между проверками",
        )
        obj = self.factory(**{field_name: non_unique_value})
        self.assertEqual(
            self.model.objects.count(), 1,
            "Вероятно, что запись объекта прошла не успешно",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.factory(**{field_name: non_unique_value})
        self.assertEqual(
            self.model.objects.count(), 1,
            "Вероятно, что объект все равно попал в базу данных",
        )

        obj.delete()
        self.assertEqual(
            self.model.objects.count(), 0,
            "Вероятно, что удаление объекта прошло не успешно",
        )
