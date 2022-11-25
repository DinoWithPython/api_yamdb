"""Сериалайзеры приложения api."""
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from reviews.models import Category, Comment, Genre, Review, Title


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров."""

    class Meta:
        """Мета класс жанра."""

        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        """Мета класс категории."""

        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class TitleReadonlySerializer(serializers.ModelSerializer):
    """Сериализатор произведений для List и Retrieve."""

    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:
        """Мета класс произведения."""

        fields = '__all__'
        model = Title

    def validate_title_year(self, value):
        """Валидация года произведения."""
        if value > timezone.now().year:
            raise ValidationError(
                ('Год выпуска %(value)s больше текущего.'),
                params={'value': value},
            )


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведений для Create, Partial_Update и Delete."""

    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    class Meta:
        """Мета класс произведения."""

        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Reviews."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        """Валидация отзыва."""
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Вы уже оставили отзыв!')
        return data

    class Meta:
        """Мета класс для ReviewsSerializer."""

        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ['title']


class CommentSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Comment."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        """Мета класс для CommentSerializer."""

        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
