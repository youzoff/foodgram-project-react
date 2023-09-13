from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.users.serializers import CustomUserSerializer
from foodgram import settings
from foodgram.settings import AMOUNT_MIN_VALUE, MIN_TIME_VALUE
from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Tag
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """
    Tag serializer
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

    def to_internal_value(self, data):
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """
    Ingredient serializer
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Serialize ingredients in recipe
    """
    # id from ingredient
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    # name from ingredient
    name = serializers.ReadOnlyField(source='ingredient.name')
    # measurement unit from ingredient
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=settings.AMOUNT_MIN_VALUE)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Recipe serializer
    """
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredient'
    )
    cooking_time = serializers.IntegerField(min_value=settings.MIN_TIME_VALUE)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['author', 'name', 'text']
            )
        ]


class RecipeReadSerializer(RecipeSerializer):
    """
    Recipe safe methods serializer
    """
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ReadOnlyField(source='image.url')

    class Meta(RecipeSerializer.Meta):
        fields = (RecipeSerializer.Meta.fields
                  + ('is_favorited', 'is_in_shopping_cart')
                  )

    def favorite_shopping_cart_fields(self, class_obj, obj):
        request = self.context.get('request')
        user = request.user
        if request and user.is_authenticated:
            return class_obj.objects.filter(recipe=obj, user=user).exists()

    def get_is_favorited(self, obj):
        return self.favorite_shopping_cart_fields(Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        return self.favorite_shopping_cart_fields(ShoppingCart, obj)


class RecipeWriteSerializer(RecipeSerializer):
    """
    Recipe create/update/destroy serializer
    """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    def validate(self, attrs):
        """
        Validation recipe fields
        """
        if not len(attrs):
            raise ValidationError(
                _('Impossible to create a recipe')
            )
        # validate ingredients
        ingredients_amount = attrs['recipe_ingredient']
        if not ingredients_amount:
            raise ValidationError(
                _('The list of ingredients cannot be empty')
            )
        unique_ingredients = set()
        for data in ingredients_amount:
            if data['amount'] < AMOUNT_MIN_VALUE:
                raise ValidationError(
                    _('The amount must be greater than or equal to ',
                      AMOUNT_MIN_VALUE
                      )
                )
            ingredient = data['ingredient']['id']
            if ingredient in unique_ingredients:
                raise ValidationError(
                    _('The ingredients must be unique')
                )
            unique_ingredients.add(ingredient)

        # validate cooking time
        if attrs['cooking_time'] < MIN_TIME_VALUE:
            raise ValidationError(
                _('The amount must be greater than or equal to ',
                  MIN_TIME_VALUE
                  )
            )

        return attrs

    def add_ingredients(self, recipe, ingredients_data):
        ingredients_list = []
        for data in ingredients_data:
            ingredient = data['ingredient']['id']
            amount = data.get('amount')
            ingredients_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(
            ingredients_list
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredient')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        self.add_ingredients(recipe, ingredients_data)

        recipe.tags.set(tags_data)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        if 'recipe_ingredient' in validated_data:
            ingredients_data = validated_data.pop('recipe_ingredient')
            instance.ingredients.clear()
            self.add_ingredients(instance, ingredients_data)

        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)
        return super().update(instance, validated_data)


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    """
    Class for Favorite and ShoppingCart serializers
    """
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')
        validators = [
            UniqueTogetherValidator(
                queryset='model.objects.all()',
                fields=['user', 'recipe']
            )
        ]


class FavoriteSerializer(FavoriteShoppingCartSerializer):
    """
    Favorite Serializer
    based on FavoriteShoppingCartSerializer
    """
    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(FavoriteShoppingCartSerializer):
    """
    Shopping Cart Serializer
    based on FavoriteShoppingCartSerializer
    """
    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart
