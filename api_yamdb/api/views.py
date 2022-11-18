"""Классы представления приложения api."""

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title, User
from .mixins import CreateListDestroyViewset
from .permissions import (IsAdmin, IsAdminModeratorOwnerOrReadOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadonlySerializer, TitleSerializer,
                          UserSerializer)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вью-класс для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вью-класс для комментариев."""

    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
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
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return TitleReadonlySerializer
        return TitleSerializer

    def update(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)

    def partial_update(self, request, *args, **kwargs):
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
    email = request.data['email']
    username = request.data['username']
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
    return Response(confirmation_code, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_token(request):
    """Вью функция для получения токена при отправке кода подтверждения."""
    user = get_object_or_404(User, username=request.data['username'])
    if not user:
        return JsonResponse(
            {'Error': 'Пользователь не найден!'},
            status=status.HTTP_404_NOT_FOUND
        )
    confirmation_code = request.data['confirmation_code']
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
    permission_classes = (IsAdmin,)
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(self.request.user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            user = get_object_or_404(User, username=self.request.user)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.data, status=status.HTTP_400_BAD_REQUEST
            )
