"""Модели приложения users."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель юзера."""

    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER_ROLE = [
        ('user', USER),
        ('admin', ADMIN),
        ('moderator', MODERATOR),
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
    )
    first_name = models.TextField('Имя', max_length=150, blank=True)
    last_name = models.TextField('Фамилия', max_length=150, blank=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль', max_length=30, choices=USER_ROLE, default='user'
    )

    @property
    def is_user(self):
        """Проверка на пользователя."""
        return self.role == self.USER

    @property
    def is_admin(self):
        """Проверка на админа."""
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        """Проверка на модератора."""
        return self.role == self.MODERATOR

    class Meta:
        """Мета класс пользователя."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)
