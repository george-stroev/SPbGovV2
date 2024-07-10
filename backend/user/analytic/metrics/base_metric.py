"""
Модуль, содержащий абстрактный класс метрики
"""
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class BaseMetric(ABC):
    """
    Абстрактный класс метрики

    Attributes:
        PARAMS_KWARGS_OBJ: Схема аргументов блока методов get_*_params
    """
    PARAMS_KWARGS_OBJ: type = BaseModel

    @abstractmethod
    def calculate(self, *args, **kwargs) -> Any:
        """Метод расчета метрики"""

    def get_params(self, project, **kwargs: PARAMS_KWARGS_OBJ) -> dict[str, Any]:
        """
        Метод получения из API необходимых
        для расчета метрики аргументов

        Args:
            project:
        """
        return getattr(self, f"get_{project.type.lower()}_params")(
            project.type_service.get_client(),
            **kwargs
        )

    def __call__(self, project, **kwargs: PARAMS_KWARGS_OBJ) -> Any:
        """
        Вызов расчета функции

        Args:
            project: Проект, в котором рассчитывается метрика
        """
        return self.calculate(**self.get_params(project=project, **kwargs))
