from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe

from users.models import Subscription

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    User create serializer
    """
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name', 'password'
        )


class CustomUserSerializer(UserSerializer):
    """
    User view serializer
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return bool(
            user.is_authenticated
            and obj.subscribed.filter(user=user).exists()
        )


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    """
    Show recipe in subscription serializer
    """
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    """
    Subscription serializer
    """
    recipes_count = serializers.ReadOnlyField(
        source='author.recipes.count'
    )
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed',
            'recipes', 'recipes_count',
        )
        read_only_fields = fields

    def get_recipes(self, obj):
        """
        Get recipes from the author the user is subscribed to
        """
        request = self.context.get('request')
        recipes_limit = (
            request.parser_context['request'].
            query_params.get('recipes_limit')
        )
        recipes = obj.author.recipes.all()[:int(recipes_limit)]
        serializer = RecipeSubscriptionSerializer(recipes, many=True)
        return serializer.data
