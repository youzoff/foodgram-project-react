from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import PageNumberLimitPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from core.utils import get_shopping_list_pdf
from .models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Tag
)
from .serializers import (
    FavoriteSerializer, IngredientSerializer,
    RecipeReadSerializer, RecipeWriteSerializer,
    ShoppingCartSerializer, TagSerializer
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = PageNumberLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def favorite_and_shopping_cart(self, **kwargs):
        request = kwargs['request']
        user = request.user
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        serializer = kwargs['serializer'](
            recipe, context={"request": request}
        )
        class_obj = kwargs['class']
        if request.method == 'POST':
            if class_obj.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': _('The recipe has already been added')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            class_obj.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        obj = class_obj.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(
                {'detail': _('Recipe removed')},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': _('Error deleting')},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        kwargs = {
            'request': request,
            'pk': pk,
            'class': Favorite,
            'serializer': FavoriteSerializer
        }
        return self.favorite_and_shopping_cart(**kwargs)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        kwargs = {
            'request': request,
            'pk': pk,
            'class': ShoppingCart,
            'serializer': ShoppingCartSerializer
        }
        return self.favorite_and_shopping_cart(**kwargs)

    @action(
        methods=['GET'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):

        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user
        )
        ingredients = recipe_ingredients.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))

        if not ingredients:
            return Response(
                {'details': _('There are no recipes in the shopping cart')},
                status=status.HTTP_400_BAD_REQUEST
            )

        context = {
            'user': request.user,
            'ingredients': ingredients
        }
        pdf = get_shopping_list_pdf(
            'api/shopping_list_pdf_template.html', context
        )
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'inline; filename="{request.user.username}_ShoppingCart.pdf"'
        )
        return response
