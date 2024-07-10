"""
Модуль, хранящий клиент доступа к redis db
"""
import pickle
from functools import wraps
from typing import Callable, Any

from redis import Redis


#pylint: disable=W0223, R0901
class RedisClient(Redis):
    """
    Клиент доступа к базе данных Redis

    Note:
        Реализован в виде Singleton

    Attributes:
        instance: Единственный экземпляр клиента
    """

    def __new__(cls) -> "RedisClient":
        """Метод, обеспечивающий реализацию Singleton"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(RedisClient, cls).__new__(cls)
        return cls.instance

    @property
    def _default_init_kwargs(self):
        return {
            "host": "redis",
            "port": 6379,
            "db": 0
        }

    def __init__(self, **kwargs):
        extra_kwargs = {
            key: kwargs.pop(key) if kwargs.get(key) else val
            for key, val in self._default_init_kwargs
        }
        super().__init__(**kwargs, **extra_kwargs)


    @staticmethod
    def get_key_by_function_with_params(function, *args, **kwargs) -> str:
        """
        Метод, генерирующий строку-ключ функции
        по ее определенной значениями сигнатуре

        Args:
            function: Функция, ключ к которой генерируется
            args: Позиционные аргументы, переданные в функцию при вызове
            kwargs: Keyword аргументы, переданные в функцию при вызове
        """
        return f"function-cache-prefix-{function.__name__}-{str(args)}-{str(kwargs)}"

    @staticmethod
    def loads(data):
        """
        Метод, используемый клиентом
        для десериализации данных

        Args:
            data: Десериализуемые данные
        """
        return pickle.loads(data)

    @staticmethod
    def dumps(data):
        """
        Метод, используемый клиентом
        для сериализации данных

        Args:
            data: Cериализуемые данные
        """
        return pickle.dumps(data)


def redis_cache(life_time: int) -> Callable[[Callable], Any]:
    """
    Функция, создающая декоратор
    временного кэширования

    Args:
        life_time: Время жизни созданного кэша
    """

    def decorator(func: Callable) -> Callable:
        """
        Декоратор, кэширующий результат работы функции,
        и использующий его при следующих ее вызовах

        Args:
            func: декорируемая функция
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Функция, оборачивающая декорируемую функций"""
            key = RedisClient.get_key_by_function_with_params(func, *args, **kwargs)
            redis_client = RedisClient()
            if redis_client.get(key) is not None:
                result = redis_client.loads(redis_client.get(key))
            else:
                result = func(*args, **kwargs)
                redis_client.setex(key, life_time, redis_client.dumps(result))
            return result

        return wrapper

    return decorator
