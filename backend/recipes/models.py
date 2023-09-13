from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from foodgram import settings

User = get_user_model()


class Tag(models.Model):
    """
    Tag model
    """
    name = models.CharField(
        _('tag name'),
        max_length=settings.CHAR_FIELD_MAX_LENGTH,
        unique=True,
        db_index=True
    )
    color = models.CharField(
        _('tag color'),
        max_length=settings.COLOR_MAX_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        _('tag slug'),
        max_length=settings.CHAR_FIELD_MAX_LENGTH,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Ingredient model
    """
    name = models.CharField(
        _('ingredient name'),
        max_length=settings.CHAR_FIELD_MAX_LENGTH,
        db_index=True
    )
    measurement_unit = models.CharField(
        _('ingredient measurement unit'),
        max_length=settings.CHAR_FIELD_MAX_LENGTH,
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('ingredient')
        verbose_name_plural = _('ingredients')
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """
    Recipe model
    """
    name = models.CharField(
        _('recipe name'),
        max_length=settings.CHAR_FIELD_MAX_LENGTH,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        verbose_name=_('recipe author'),
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    text = models.TextField(_('recipe text'))
    image = models.ImageField(
        _('recipe image'),
        upload_to='recipes/images/',
    )
    cooking_time = models.PositiveSmallIntegerField(
        _('cooking time'),
        validators=[MinValueValidator(settings.MIN_TIME_VALUE)],
        default=settings.MIN_TIME_VALUE,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name=_('recipe tag'),
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient', 'recipes__measurement_unit'),
        related_name='recipes',
        verbose_name=_('recipe ingredients'),
    )
    pub_date = models.DateTimeField(
        _('publication date'),
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date', 'name']
        verbose_name = _('recipe')
        verbose_name_plural = _('recipes')
        constraints = [models.UniqueConstraint(
            fields=['author', 'name', 'text'],
            name='unique_recipe_author'
        )]

    def __str__(self):
        return f'{self.name} @{self.author}'


class RecipeIngredient(models.Model):
    """
    Model for communicate Recipe and Ingredient
    """
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredient',
        verbose_name=_('recipe with ingredient'),
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredient',
        verbose_name=_('ingredient in recipe'),
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        _('ingredient amount'),
        validators=[MinValueValidator(settings.AMOUNT_MIN_VALUE)],
        default=settings.AMOUNT_MIN_VALUE
    )

    class Meta:
        verbose_name = _('recipe ingredient')
        verbose_name_plural = _('recipe ingredients')
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredient'
        )]

    def __str__(self):
        return f'{self.ingredient.name} -> {self.recipe.name}'


class UserRecipe(models.Model):
    """
    Model to display Recipe in User panel
    """
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('recipe'),
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        _('date added'),
        auto_now_add=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        return (
            f'{self.recipe.name} in {self.user.get_username()} '
            + self._meta.verbose_name
        )


class Favorite(UserRecipe):
    """
    Favorite model
    """
    class Meta:
        ordering = ['-pub_date']
        verbose_name = _('favorite')
        verbose_name_plural = _('favorites')
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_recipe_user_favorite'
        )]


class ShoppingCart(UserRecipe):
    """
    Shopping cart model
    """
    class Meta:
        ordering = ['-pub_date']
        verbose_name = _('shopping cart')
        verbose_name_plural = _('shopping cart')
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_recipe_user_shopping_cart'
        )]
