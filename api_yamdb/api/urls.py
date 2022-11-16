from django.urls import include, path
from rest_framework import routers

from . import views

urlspatterns = [
    path('v1/auth/signup/', views.send_confirmation_code),
    path('v1/auth/token/', views.send_token),
]
