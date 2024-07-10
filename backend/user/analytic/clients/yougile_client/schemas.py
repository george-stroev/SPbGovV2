"""
Модуль, содержащий схемы, используемые
при работе YouGile клиента
"""
from pydantic import BaseModel, field_serializer


def paginated(schema: type) -> type:
    """
    Функция, создающая схему пагинированного списка
    объектов, на основе одного объекта

    Args:
        schema:
            Объект, используемый для пагинации
    """

    class Paging(BaseModel):
        """
        Схема, отвечающая за сохранение
        информации о состоянии пагинации

        Attributes:
            count: Общее количество объектов в выборке
            limit: Количество объектов на странице
            offset: Номер объекта, с которого начинаются объекты на страницы
            next: Есть ли следующие страницы
        """
        count: int
        limit: int
        offset: int
        next: bool

    class PaginatedSchema(BaseModel):
        """
        Схема контейнера пагинации

        Attributes:
            paging: Схема состояния пагинации
            content: Список пагинированных объектов
        """
        paging: Paging
        content: list[schema]

    return PaginatedSchema


class Task(BaseModel):
    """
    Обобщенная схема 'задачи', приходящей из YouGile API

    Attributes:
        completed: Завершена ли задача
        assigned: Список UUID пользователей, подписанных на задачу
    """
    completed: bool
    assigned: list[str] | str = []

    #pylint: disable=E0213
    @field_serializer('assigned')
    def serialize_assigned(assigned: list[str] | str) -> list[str]:
        """
        Метод, проводящий сериализацию списка подписчиков задачи

        Поскольку, если подписчик только один, то приходит
        не список, а строка, необходимо привести
        это к единому виду

        Args:
            assigned: Текущий список подписчиков задачи
        """
        return assigned if isinstance(assigned, list) else list[assigned]


class Employee(BaseModel):
    """
    Обобщенная схема 'работника', приходящего из YouGile API

    Attributes:
        id: Идентификатор работника
        email: Почтовый ящик работника
        realName: Имя работника
    """
    id: str
    email: str
    realName: str
