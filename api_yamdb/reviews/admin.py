"""Админ панель."""

from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Review, Title

reviews_models = [Category, Comment, Genre, GenreTitle, Review, Title]
admin.site.register(reviews_models)
