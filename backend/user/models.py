"""
Модуль, содержащий ORM классы,
определяющие таблицы базы данных
"""
from abc import ABC, abstractmethod
from importlib.resources import _
from typing import Any, cast

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
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

    last_login = models.DateTimeField(_("Дата последнего посещения"), blank=True, null=True)

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("Логин"),
        max_length=150,
        unique=True,
        help_text=_("Требуется не более 150 символов. Только буквы, цифры и @/./+/-/_."),
        validators=[username_validator],
        error_messages={
            "unique": _("Это имя пользователя уже существует."),
        },
    )
    password = models.CharField(_("Пароль"), max_length=128)
    first_name = models.CharField(_("Имя"), max_length=150, blank=True)
    last_name = models.CharField(_("Фамилия"), max_length=150, blank=True)
    email = models.EmailField(blank=True)
    is_staff = models.BooleanField(
        _("Администраторские права"),
        default=False,
        help_text=_("Определяет, может ли пользователь войти на этот административный сайт."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Определяет, следует ли считать этого пользователя активным. "
            "Снимите этот флажок вместо удаления учетных записей."
        ),
    )
    date_joined = models.DateTimeField(_("Дата регистрации"), default=timezone.now)

    # pylint: disable=missing-docstring
    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")


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
        client = cast(YouGileClient, self.get_client())
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
    type: str = models.CharField(
        _("Тип клиента"), max_length=16, choices=Services,
        help_text=_("Название сервиса, который будет использоваться для аналитики"),
    )
    token: str = models.CharField(
        _("Ключ"), max_length=255,
        help_text=_(
            "Ключ доступа, по которому можно получить "
            "необходимые данные из сервиса "
            "(Нужно получить из сервиса)"
        ),
    )
    user: "user.User" = models.ForeignKey(
        'user.User', verbose_name=_("Пользователь"), on_delete=models.PROTECT,
        help_text=_("Пользователь, которому принадлежат права доступа к проекту"),
    )

    @property
    def type_service(self) -> BaseProjectTypeService:
        """Метод получения сервиса в зависимости от типа"""
        return {
            Services.YOUGILE: YouGileTypeService
        }[self.type](self)

    # pylint: disable=missing-docstring
    class Meta:
        verbose_name = _("Проект")
        verbose_name_plural = _("Проекты")


class Employee(ExplicitModel):
    """Модель, отвечающая за хранение информации по сотрудникам проекта"""
    ref_id: str = models.CharField(
        _("ID объекта в сервисе"), max_length=255, unique=True,
        help_text=_("Уникальный идентификатор объекта, используемый сервисом для его определения"),
    )
    email: str = models.EmailField()
    name: str = models.CharField(_("Имя"), max_length=255)
    project: 'user.Project' = models.ForeignKey(
        'user.Project', verbose_name=_("Рабочий проект"), on_delete=models.PROTECT,
        help_text=_("Проект, в котором работает сотрудник"),
    )

    # pylint: disable=missing-docstring
    class Meta:
        verbose_name = _("Сотрудник")
        verbose_name_plural = _("Сотрудники")
