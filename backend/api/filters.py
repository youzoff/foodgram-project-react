from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def is_favorited_filter(self, queryset, name, value):
        return (
            queryset.filter(favorite__user=self.request.user)
            if value and self.request.user.is_authenticated
            else queryset
        )

    def is_in_shopping_cart_filter(self, queryset, name, value):
        return (
            queryset.filter(shoppingcart__user=self.request.user)
            if value and self.request.user.is_authenticated
            else queryset
        )


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
