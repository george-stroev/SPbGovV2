"""Модуль, содержащий viewsers данного проекта"""
from django.contrib.auth import authenticate
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.analytic.metrics.count_of_complete_tasks import CountOfCompleteTasks
from user.models import Employee, User, Project
from user.permissions import IsYourEmployeePermission, IsYourProjectPermission
from user.serializers import EmployeeSerializer, UserSerializer, ProjectSerializer


# pylint: disable=C0115
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        """
        Определяет сериализатор в зависимости от метода
        """
        return {
            self.login.__name__: AuthTokenSerializer,
        }.get(self.action, UserSerializer)

    @action(methods=['post'], detail=False, permission_classes=[AllowAny])
    def register(self, request):
        """Конечная точка регистрации пользователя"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(methods=['post'], detail=False, permission_classes=[AllowAny])
    def login(self, request):
        """Конечная точка входа в систему"""
        user = authenticate(
            request,
            username=request.data['username'],
            password=request.data['password'],
        )
        if user:
            # pylint: disable=E1101
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'email': user.email,
                'username': user.username,
            })
        return Response({'error': 'Invalid credentials'}, status=401)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Конечная точка выхода из системы"""
        if request.user.auth_token:
            request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'}, status=204)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsYourEmployeePermission]

    # @swagger_auto_schema(
    #     query_serializer=None,
    #     manual_parameters=[
    #         openapi.Parameter(
    #             'my_new_query_param',
    #             openapi.IN_QUERY,
    #             description="The new query param",
    #             type=openapi.TYPE_STRING,
    #         ),
    #         openapi.Parameter(
    #             'my_other_query_param',
    #             openapi.IN_QUERY,
    #             description="Another query param",
    #             type=openapi.TYPE_BOOLEAN,
    #         )
    #     ],
    # )
    # pylint: disable=W0613
    @action(detail=True, methods=['get'])
    def count_of_complete_tasks(self, request, pk=None):
        """Метод расчета метрики количества выполненных сотрудником задач"""
        employee = self.get_object()
        return Response(CountOfCompleteTasks()(
            project=employee.project,
            employee=employee
        ))


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsYourProjectPermission]

    # pylint: disable=W0613
    @action(detail=True, methods=['get'])
    def update_employers(self, request, pk=None):
        """Метод обновления сотрудников проекта"""
        project = self.get_object()
        project.type_service.update_employers()
        return Response("Success!!!")
