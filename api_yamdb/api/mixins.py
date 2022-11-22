"""Миксины."""

from rest_framework import filters, mixins, viewsets

from .permissions import IsAdminOrReadOnly


class CreateListDestroyViewset(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Класс миксин создания и удаления."""

    serializer_class = None
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
