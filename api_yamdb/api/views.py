from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User, Category, Genre, Title, Review, Comment


@api_view(["POST"])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    email = request.data["email"]
    username = request.data["username"]
    user = User.objects.create(
        email=email,
        username=username
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        "Код подтверждения",  # Тема письма
        f"{confirmation_code}",  # Тело письма
        f"{settings.ADMIN_EMAIL}",  # От кого
        [f"{email}"],  # Кому письмо
        fail_silently=False,
    )
    return Response(confirmation_code, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def send_token(request):
    user = get_object_or_404(User, username=request.data["username"])
    if not user:
        return JsonResponse(
            {"Error": "Пользователь не найден!"},
            status=status.HTTP_404_NOT_FOUND
    )
    confirmation_code = request.data["confirmation_code"]
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
        {"Error": "Проверьте код подтверждения"},
        status=status.HTTP_400_BAD_REQUEST
    )
