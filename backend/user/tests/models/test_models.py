"""Модуль, содержащий тесты моделей"""
from unittest.mock import patch

from django.test import TestCase

from user.analytic.clients.yougile_client import YouGileClient, schemas
from user.factories import ProjectFactory, EmployeeFactory
from user.models import Project, Employee, YouGileTypeService, Services
from user.tests.models.model_assert_pack import BaseModelFieldsTestPack, field_test_pack


# pylint: disable=missing-class-docstring
class TestProjectFields(BaseModelFieldsTestPack):
    factory = ProjectFactory
    model = Project

    @field_test_pack("token")
    def test_token(self, field_name: str):
        """Функциональные тесты поля token"""
        self.assert_char_field_length(
            field_name=field_name,
            expected_max_length=255,
        )


# pylint: disable=missing-class-docstring
class TestEmployeeFields(BaseModelFieldsTestPack):
    factory = EmployeeFactory
    model = Employee

    @field_test_pack("ref_id")
    def test_ref_id(self, field_name: str):
        """Функциональные тесты поля ref_id"""
        self.assert_char_field_length(
            field_name=field_name,
            expected_max_length=255,
        )
        self.assert_unique_value(field_name=field_name)

    @field_test_pack("name")
    def test_name(self, field_name: str):
        """Функциональные тесты поля name"""
        self.assert_char_field_length(
            field_name=field_name,
            expected_max_length=255,
        )


# pylint: disable=missing-class-docstring
class TestProject(TestCase):
    factory = ProjectFactory
    model = Project

    def test_type_service(self):
        """Проверяет правильность получения type сервиса"""
        cases = {
            Services.YOUGILE: YouGileTypeService,
        }
        with self.subTest():
            for key, val in cases.items():
                self.assertEqual(self.model.objects.count(), 0)
                project = self.factory(type=key)
                self.assertIsInstance(project.type_service, val)
                project.delete()


# pylint: disable=missing-class-docstring
class TestYouGileTypeService(TestCase):

    def test_get_token(self):
        """Проверяет правильность преобразований над токеном"""
        project = ProjectFactory()
        self.assertEqual(project.type_service.get_token(), project.token)

    def test_update_employers(self):
        """Проверяет обновление сотрудников"""
        employee: Employee = EmployeeFactory()
        current_project: Project = employee.project
        with patch.object(
                YouGileClient, "get_employers",
                return_value=schemas.paginated(schemas.Employee)(**{
                    "paging": {
                        "count": 2,
                        "limit": 50,
                        "offset": 0,
                        "next": False,
                    },
                    "content": [
                        {
                            "id": employee.ref_id,
                            "email": employee.email,
                            "realName": employee.name
                        },
                        {
                            "id": "fake_id",
                            "email": "fake_email@mail.ru",
                            "realName": "Fake George",
                        },
                    ]
                })
        ) as _:
            self.assertEqual(Employee.objects.count(), 1)
            current_project.type_service.update_employers()
            self.assertEqual(Employee.objects.count(), 2)

    def test_get_client(self):
        """Проверяет возможность получить клиент"""
        project = ProjectFactory()
        self.assertIsInstance(project.type_service.get_client(), YouGileClient)
