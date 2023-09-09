from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import CustomUserSerializer
from .models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Tag
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

    def to_internal_value(self, data):
        return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredient'
    )
    cooking_time = serializers.IntegerField(min_value=1)
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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(RecipeSerializer.Meta):
        fields = (
            RecipeSerializer.Meta.fields
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
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    def validate_ingredients(self, ingredients):
        if not len(ingredients):
            raise ValidationError(
                'The list of ingredients cannot be empty'
            )
        unique_ingredients = set()
        for ingredient in ingredients:
            ingredient_id = ingredient['ingredient']['id']
            if ingredient_id in unique_ingredients:
                raise ValidationError(
                    'The ingredients must be unique'
                )
            unique_ingredients.add(ingredient_id)
        return ingredients

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
        return ingredients_list

    def add_tags(self, tags_data):
        tags_list = []
        for tag_id in tags_data:
            tag = get_object_or_404(Tag, id=tag_id)
            tags_list.append(tag)
        return tags_list

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredient')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        ingredients = self.add_ingredients(recipe, ingredients_data)
        RecipeIngredient.objects.bulk_create(
            ingredients
        )

        tags = self.add_tags(tags_data)
        recipe.tags.set(tags)

        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        if 'recipe_ingredient' in validated_data:
            ingredients_data = validated_data.pop('recipe_ingredient')
            instance.ingredients.clear()
            ingredients = self.add_ingredients(instance, ingredients_data)
            RecipeIngredient.objects.bulk_create(
                ingredients
            )
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            tags = self.add_tags(tags_data)
            instance.tags.set(tags)
        return super().update(instance, validated_data)


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
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
    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(FavoriteShoppingCartSerializer):
    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart
