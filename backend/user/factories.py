"""Модуль, содержащий фабрики текущего проекта"""
import factory

from user.models import Services


ExplicitFactory = factory.django.DjangoModelFactory


# pylint: disable=missing-class-docstring
class UserFactory(ExplicitFactory):
    # pylint: disable=missing-docstring
    class Meta:
        model = 'user.User'

    username = factory.sequence(lambda n: f"fake_username #{n}")
    first_name = "Fake George"
    last_name = "Fake Smith"
    email = "fake_email@mail.ru"
    is_staff = False
    is_active = True


# pylint: disable=missing-class-docstring
class ProjectFactory(ExplicitFactory):

    # pylint: disable=missing-docstring
    class Meta:
        model = 'user.Project'

    type = Services.YOUGILE
    token = "_".join(["fake_token"] * 20)
    user = factory.SubFactory('user.factories.UserFactory')


class EmployeeFactory(ExplicitFactory):

    class Meta:
        model = 'user.Employee'

    ref_id = factory.sequence(lambda n: f"ref_id #{n}")
    email = "fake_email@mail.ru"
    name = "Fake George"
    project = factory.SubFactory('user.factories.ProjectFactory')
