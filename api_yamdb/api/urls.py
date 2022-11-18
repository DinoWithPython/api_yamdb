"""Эндпоинты api."""

from django.urls import path, include
from rest_framework import routers

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
    send_confirmation_code,
    send_token,
)

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet, basename='user')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('titles', TitleViewSet, basename='titles')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', send_confirmation_code),
    path('v1/auth/token/', send_token),
]
