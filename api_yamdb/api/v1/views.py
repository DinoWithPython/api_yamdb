"""Классы представления приложения api."""

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, viewsets
from rest_framework import filters, viewsets
from rest_framework.response import Response
from reviews.models import Category, Genre, Title

from .filters import TitlesFilter
from .mixins import CreateListDestroyViewset
from .permissions import (IsAdminModeratorOwnerOrReadOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadonlySerializer, TitleSerializer)


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
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        try:
            review = title.reviews.get(id=self.kwargs.get('review_id'))
            return review.comments.all()
        except TypeError:
            TypeError('У произведения нет такого отзыва!')

    def perform_create(self, serializer):
        """Переопределение создания класса CommentViewSet."""
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        try:
            review = title.reviews.get(id=self.kwargs.get('review_id'))
            serializer.save(author=self.request.user, review=review)
        except TypeError:
            TypeError('У произведения нет такого отзыва!')


class GenreViewSet(CreateListDestroyViewset):
    """Вью-класс для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewset):
    """Вью-класс для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = "slug"


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
