"""Модуль, содержащий класс функции расчета метрики"""
from typing import Any

from pydantic import BaseModel

from .base_metric import BaseMetric


class Employee(BaseModel):
    """Схема для приходящего объекта сотрудника"""
    ref_id: str


class KwargsObj(BaseModel):
    """Схема аргументов get_*_params методов функции"""
    employee: Employee


class CountOfCompleteTasks(BaseMetric):
    """
    Класс расчета метрики количества
    выполненных задач на сотрудника

    Attributes:
        PARAMS_KWARGS_OBJ: Схема аргументов блока методов get_*_params
    """
    PARAMS_KWARGS_OBJ: type = KwargsObj

    @staticmethod
    def get_yougile_params(client, **kwargs: PARAMS_KWARGS_OBJ) -> dict[str, Any]:
        """
        Получение параметров функции и API YouGile

        Args:
            client: YouGile клиент для взаимодействия с API
        """
        employee = kwargs.pop('employee')
        tasks = client.get_tasks().content
        return {"employee": employee, "tasks": tasks}

    #pylint: disable=W0221
    def calculate(self, employee: Employee, tasks) -> int:
        """
        Метод расчета метрики количества выполненных задач

        Args:
            employee: сотрудник, задачи которого учитываются
            tasks: Задачи, идущие в учет
        """
        return len([
            task for task in tasks
            if task.completed and employee.ref_id in task.assigned
        ])
