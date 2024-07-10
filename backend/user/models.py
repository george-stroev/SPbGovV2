"""
Модуль, содержащий ORM классы,
определяющие таблицы базы данных
"""
from abc import ABC, abstractmethod
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db import models

from user.analytic.clients.base_client import BaseClient
from user.analytic.clients.yougile_client import YouGileClient


class ExplicitModel(models.Model):
    """
    Модель, явно определяющая параметры,
    генерируемые BaseModel

    Attributes:
        objects: Менеджер взаимодействия с базой данных
    """
    objects: models.Manager

    # pylint: disable=C0115
    class Meta:
        abstract = True


class User(AbstractUser):
    """Модель пользователя"""


class Services(models.TextChoices):
    """
    Класс, формирующий перечисление сервисов,
    с которыми взаимодействует приложение
    """
    YOUGILE = "Yougile"


class BaseProjectTypeService(ABC):
    """
    Интерфейс класса, отвечающего за взаимодействие
    проекта с различными клиентами сервисов
    """

    @abstractmethod
    def get_token(self) -> Any:
        """Метод получения токена (он может быть зашифрован, например)"""

    @abstractmethod
    def update_employers(self) -> None:
        """Метод обновления сотрудников в текущем проекте"""

    @abstractmethod
    def get_client(self) -> BaseClient:
        """Метод получения клиента по проекту"""


class YouGileTypeService(BaseProjectTypeService):
    """
    Интерфейс класса, отвечающего за взаимодействие
    проекта с YouGile клиентом
    """
    def __init__(self, project: "user.Project"):
        """
        Args:
             project: Проект, с которым взаимодействует сервис
        """
        self.project = project

    def get_token(self) -> str:
        """Метод получения токена (он может быть зашифрован, например)"""
        return self.project.token

    def update_employers(self):
        """Метод обновления сотрудников в текущем проекте"""
        next_ = True
        client = self.get_client()
        existed_employers_objs = Employee.objects\
            .filter(project__id=self.project.id)\
            .in_bulk(field_name='ref_id')
        new_employers_objs = {}
        offset, limit = 0, 50
        while next_:
            response = client.get_employers(limit=limit, offset=offset)
            offset += limit

            for employee in response.content:
                values = {
                    'email': employee.email,
                    'name': employee.realName,
                    'project': self.project,
                }
                if existed_employers_objs.get(employee.id):
                    for key, val in values.items():
                        setattr(existed_employers_objs.get(employee.id), key, val)
                else:
                    new_employers_objs[employee.id] = Employee(
                        ref_id=employee.id,
                        **values,
                    )

            next_ = response.paging.next

        Employee.objects.bulk_update(
            list(existed_employers_objs.values()),
            fields=['email', 'name', 'project'],
        )
        Employee.objects.bulk_create(list(new_employers_objs.values()))

    def get_client(self) -> BaseClient:
        """Метод получения клиента по проекту"""
        return YouGileClient(token=self.get_token())


class Project(ExplicitModel):
    """
    Модель, отвечающая за хранение информации
    о проектах, с которыми работает пользователь
    """
    type: str = models.CharField(max_length=16, choices=Services)
    token: str = models.CharField(max_length=255)
    user: "user.User" = models.ForeignKey('user.User', on_delete=models.PROTECT)

    @property
    def type_service(self) -> BaseProjectTypeService:
        """Метод получения сервиса в зависимости от типа"""
        return {
            Services.YOUGILE: YouGileTypeService
        }[self.type](self)


class Employee(ExplicitModel):
    """Модель, отвечающая за хранение информации по сотрудникам проекта"""
    ref_id: str = models.CharField(max_length=255, unique=True)
    email: str = models.EmailField()
    name: str = models.CharField(max_length=255)
    project: 'user.Project' = models.ForeignKey('user.Project', on_delete=models.PROTECT)
