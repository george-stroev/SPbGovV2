from unittest.mock import patch, Mock

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.viewsets import ModelViewSet

from user.analytic.metrics.count_of_complete_tasks import CountOfCompleteTasks
from user.factories import UserFactory, ProjectFactory, EmployeeFactory
from user.models import Project, ExplicitModel
from user.serializers import ProjectSerializer
from user.views import ProjectViewSet, UserViewSet, EmployeeViewSet


# pylint: disable=missing-class-docstring
class TestEmployeeViewSet(APITestCase):
    viewset = EmployeeViewSet
    factory = EmployeeFactory
    link = "/api/v1/employee/"

    def test_count_of_complete_tasks(self):
        response_value = 18
        employee = self.factory()
        with patch.object(self.viewset, 'get_permissions', return_value=[]):
            with patch.object(CountOfCompleteTasks, '__call__', return_value=response_value):
                response = self.client.get(f"{self.link}{employee.id}/count_of_complete_tasks/")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, response_value)


# pylint: disable=missing-class-docstring
class TestProjectViewSet(APITestCase):
    model: type[ExplicitModel] = Project
    viewset: type[ModelViewSet] = ProjectViewSet
    serializer = ProjectSerializer
    factory = ProjectFactory
    link = '/api/v1/project/'

    def test_project_create(self):
        with patch.object(self.viewset, 'get_permissions', return_value=[]):
            project = self.factory()
            serialized_data = self.serializer(data=project)
            serialized_data.is_valid(raise_exception=True)
            data = serialized_data.initial_data
            project.delete()
            self.assertEqual(self.model.objects.count(), 0)
            response = self.client.post(f'{self.link}', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(self.model.objects.count(), 1)

    def test_update_employers(self):
        project = self.factory()
        with patch.object(self.model, 'type_service', return_value=Mock()):
            with patch.object(self.viewset, 'get_permissions', return_value=[]):
                response = self.client.get(f"{self.link}{project.id}/update_employers/")
                self.assertEqual(response.status_code, 200)


# pylint: disable=missing-class-docstring
class TestUserViewSet(APITestCase):
    viewset = UserViewSet

    def test_student_login(self):
        """
        Проверка аутентификации пользователя
        """
        form_data = {
            'username': 'existinguser',
            'password': 'testpassword123',
        }
        UserFactory(**form_data)
        response = self.client.post('/api/v1/user/login/', form_data, format="json")
        self.assertEqual(response.status_code, 200)

        form_data['password'] = 'testpassword'
        response = self.client.post('/api/v1/user/login/', form_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_student_register(self):
        form_data = {
            'username': 'existinguser',
            'password': 'testpassword123',
        }
        response = self.client.post('/api/v1/user/register/', form_data, format='json')
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/api/v1/user/register/', form_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_student_logout(self):
        form_data = {
            'username': 'existinguser',
            'password': 'testpassword123',
        }
        user = UserFactory(**form_data)
        response = self.client.post('/api/v1/user/login/', form_data, format="json")
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/api/v1/user/logout/', form_data, format='json',
                                    headers={"Authorization": f"Token {user.auth_token}"})
        self.assertEqual(response.status_code, 204)
        response = self.client.post('/api/v1/user/logout/', form_data, format='json',
                                    headers={"Authorization": f"Token {user.auth_token}"})
        self.assertEqual(response.status_code, 401)
