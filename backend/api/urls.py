from django.urls import include, path
from rest_framework import routers

from .recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from .users.views import CustomUserViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
