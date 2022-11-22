"""Валидаторы."""

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_title_year(value):
    """Валидация года произведения."""
    if value > timezone.now().year:
        raise ValidationError(
            ('Год выпуска %(value)s больше текущего.'),
            params={'value': value},
        )


def validate_username(value):
    """Валидация имени пользователя."""
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя "me" запрещено.'),
            params={'value': value},
        )
