from django.contrib import admin
from django.urls import include, path

from api.views import index, CustomUserViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('index', index),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
