"""
Модуль, содержащий класс YouGile клиента
"""
from typing import Any

import requests

from user.analytic.clients.base_client import BaseClient
from user.analytic.clients.redis_client import redis_cache
from user.analytic.clients.yougile_client.schemas import paginated, Task, Employee


class YouGileClient(BaseClient):
    """
    Класс YouGile клиента. Отвечает за
    предоставление унифицированного
    доступа к YouGile API
    """
    def __init__(self, token: str):
        """
        Args:
             token: Bearer токен, необходимый для подключения к API
        """
        self._token = token

    def _get_minimal_headers(self) -> dict[str, Any]:
        """
        Метод, подготавливающий минимально
        необходимые headers, для общения с API
        """
        return {
            'Authorization': f'Bearer {self._token}',
            'Content-Type': 'application/json'
        }

    # pylint: disable=R0913
    @redis_cache(10)
    def _get_tasks(
            self,
            column_id: str = "",
            include_deleted: bool = False,
            limit: int = 50,
            offset: int = 0,
            title: str = "",
    ) -> dict[str, Any]:
        """
        Метод, производящий запрос к конечной
        точке, предоставляющей список задач

        Note:
            Важно отметить, что отдельный метод
            существует для декорирования посредством redis_cache,
            который, в свою очередь, на время запоминает
            результат для последующего перепредоставления

        Args:
            column_id:
                Идентификатор колонки(берется из API),
                из которой нужно получить задачи
            include_deleted: Включать ли в список удаленные задачи
            limit: Количество задач на странице
            offset: С какой задачи по ее номеру в списке начнется страница
            title: Название задачи
        """
        # pylint: disable=W3101
        json = requests.get(
            "https://ru.yougile.com/api-v2/tasks",
            headers=self._get_minimal_headers(),
            params={
                "columnId": column_id,
                "includeDeleted": include_deleted,
                "limit": limit,
                "offset": offset,
                "title": title,
            }
        ).json()
        return json

    # pylint: disable=R0913
    def get_tasks(
            self,
            column_id: str = "",
            include_deleted: bool = False,
            limit: int = 50,
            offset: int = 0,
            title: str = "",
    ) -> paginated(Task):
        """
        Метод, производящий запрос к конечной
        точке, предоставляющей список задач

        Args:
            column_id:
                Идентификатор колонки (берется из API),
                из которой нужно получить задачи
            include_deleted: Включать ли в список удаленные задачи
            limit: Количество задач на странице
            offset: С какой задачи по ее номеру в списке начнется страница
            title: Название задачи
        """
        json = self._get_tasks(
            column_id=column_id,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
            title=title,
        )
        schema = paginated(Task)(**json)
        return schema

    @redis_cache(10)
    def _get_employers(
            self,
            email: str = "",
            limit: int = 50,
            offset: int = 0,
            project_ref_id: str = "",
    ) -> dict[str, Any]:
        """
        Метод, производящий запрос к конечной
        точке, предоставляющей список сотрудников

        Note:
            Важно отметить, что отдельный метод
            существует для декорирования посредством redis_cache,
            который, в свою очередь, на время запоминает
            результат для последующего перепредоставления

        Args:
            email: Почта сотрудника
            limit: Количество сотрудника на странице
            offset: С какого сотрудника по его номеру в списке начнется страница
            project_ref_id:
                Идентификатор проекта (берется из API),
                сотрудников которого мы хотим получить
        """
        # pylint: disable=W3101
        json = requests.get(
            "https://ru.yougile.com/api-v2/users",
            headers=self._get_minimal_headers(),
            params={
                "email": email,
                "limit": limit,
                "offset": offset,
                "projectId": project_ref_id,
            }
        ).json()
        return json

    def get_employers(
            self,
            email: str = "",
            limit: int = 50,
            offset: int = 0,
            project_ref_id: str = None,
    ) -> paginated(Employee):
        """
        Метод, производящий запрос к конечной
        точке, предоставляющей список сотрудников

        Args:
            email: Почта сотрудника
            limit: Количество сотрудника на странице
            offset: С какого сотрудника по его номеру в списке начнется страница
            project_ref_id:
                Идентификатор проекта (берется из API),
                сотрудников которого мы хотим получить
        """
        json = self._get_employers(
            email=email,
            limit=limit,
            offset=offset,
            project_ref_id=project_ref_id,
        )
        schema = paginated(Employee)(**json)
        return schema
