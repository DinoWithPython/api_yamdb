"""Классы представления приложения api."""

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitlesFilter
from .mixins import CreateListDestroyViewset
from .permissions import (IsAdmin, IsAdminModeratorOwnerOrReadOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, MeSerializer, ReviewSerializer,
                          TitleReadonlySerializer, TitleSerializer,
                          TokenSerializer, UserSerializer)


class ReviewViewSet(viewsets.ModelViewSet):
    """Класс представления Review."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        """Переопределение получения класса ReviewViewSet."""
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        """Переопределение создания класса ReviewViewSet."""
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Класс представления Comment."""

    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        """Переопределение получения класса CommentViewSet."""
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        """Переопределение создания класса CommentViewSet."""
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)


class GenreViewSet(CreateListDestroyViewset):
    """Вью-класс для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CreateListDestroyViewset):
    """Вью-класс для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вью-класс для произведений."""

    queryset = (
        Title.objects.all().annotate(Avg('reviews__score')).order_by('name')
    )
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        """Получение произведений."""
        if self.action in ('retrieve', 'list'):
            return TitleReadonlySerializer
        return TitleSerializer

    def update(self, request, *args, **kwargs):
        """Обновление произведения."""
        raise exceptions.MethodNotAllowed(request.method)

    def partial_update(self, request, *args, **kwargs):
        """Обновление произведения."""
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    """Вью функция для получения кода подтверждения."""
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = request.data.get('email')
    username = request.data.get('username')
    user = User.objects.create(
        email=email,
        username=username,
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Код подтверждения',  # Тема письма
        f'{confirmation_code}',  # Тело письма
        f'{settings.ADMIN_EMAIL}',  # От кого
        [f'{email}'],  # Кому письмо
        fail_silently=False,
    )
    return Response(
        {'email': email, 'username': username},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_token(request):
    """Вью функция для получения токена при отправке кода подтверждения."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    try:
        user = User.objects.get(username=data['username'])
    except User.DoesNotExist:
        return Response(
            {'username': 'Пользователь не найден!'},
            status=status.HTTP_404_NOT_FOUND
        )

    confirmation_code = request.data.get('confirmation_code')
    refresh = RefreshToken.for_user(user)

    anwser = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    if default_token_generator.check_token(user, confirmation_code):
        user.is_active = True
        user.save()
        return JsonResponse(anwser)
    return JsonResponse(
        {'Error': 'Проверьте код подтверждения'},
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    """Вью-класс для пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', )
    permission_classes = (IsAdmin,)
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        """Получение или обновление пользователя."""
        user = get_object_or_404(User, username=self.request.user)
        serializer = MeSerializer(self.request.user)

        if request.method == 'PATCH':
            serializer = MeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)
