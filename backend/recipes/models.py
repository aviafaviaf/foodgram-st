from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

from .constants import (
    INGREDIENT_NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    RECIPE_IMAGE_UPLOAD_PATH,
    MIN_INGREDIENT_AMOUNT,
    INGREDIENT_AMOUNT_ERROR,

    RECIPE_VERBOSE_NAME,
    RECIPE_VERBOSE_NAME_PLURAL,
    RECIPE_ORDERING,
    RECIPE_FIELD_AUTHOR,
    RECIPE_FIELD_NAME,
    RECIPE_FIELD_IMAGE,
    RECIPE_FIELD_TEXT,
    RECIPE_FIELD_COOKING_TIME,
    RECIPE_FIELD_COOKING_TIME_HELP,
    RECIPE_FIELD_INGREDIENTS,

    INGREDIENT_VERBOSE_NAME,
    INGREDIENT_VERBOSE_NAME_PLURAL,
    INGREDIENT_FIELD_NAME,
    INGREDIENT_FIELD_UNIT,
    INGREDIENT_CONSTRAINT_NAME,

    RECIPE_INGREDIENT_VERBOSE_NAME,
    RECIPE_INGREDIENT_VERBOSE_NAME_PLURAL,
    RECIPE_INGREDIENT_FIELD_AMOUNT,
    RECIPE_INGREDIENT_CONSTRAINT_NAME,

    FAVORITE_VERBOSE_NAME,
    FAVORITE_VERBOSE_NAME_PLURAL,
    FAVORITE_FIELD_USER,
    FAVORITE_FIELD_RECIPE,
    FAVORITE_CONSTRAINT_NAME,

    CART_VERBOSE_NAME,
    CART_VERBOSE_NAME_PLURAL,
    CART_FIELD_USER,
    CART_FIELD_RECIPE,
    CART_CONSTRAINT_NAME,
)

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=RECIPE_FIELD_AUTHOR
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name=RECIPE_FIELD_NAME
    )
    image = models.ImageField(
        upload_to=RECIPE_IMAGE_UPLOAD_PATH,
        verbose_name=RECIPE_FIELD_IMAGE
    )
    text = models.TextField(
        verbose_name=RECIPE_FIELD_TEXT
    )
    cooking_time = models.PositiveIntegerField(
        help_text=RECIPE_FIELD_COOKING_TIME_HELP,
        verbose_name=RECIPE_FIELD_COOKING_TIME
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name=RECIPE_FIELD_INGREDIENTS
    )

    class Meta:
        ordering = RECIPE_ORDERING
        verbose_name = RECIPE_VERBOSE_NAME
        verbose_name_plural = RECIPE_VERBOSE_NAME_PLURAL

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name=INGREDIENT_FIELD_NAME
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name=INGREDIENT_FIELD_UNIT
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name=INGREDIENT_CONSTRAINT_NAME
            )
        ]
        verbose_name = INGREDIENT_VERBOSE_NAME
        verbose_name_plural = INGREDIENT_VERBOSE_NAME_PLURAL

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name=RECIPE_VERBOSE_NAME
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name=INGREDIENT_VERBOSE_NAME
    )
    amount = models.IntegerField(
        verbose_name=RECIPE_INGREDIENT_FIELD_AMOUNT,
        validators=[
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=INGREDIENT_AMOUNT_ERROR
            )
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name=RECIPE_INGREDIENT_CONSTRAINT_NAME
            )
        ]
        verbose_name = RECIPE_INGREDIENT_VERBOSE_NAME
        verbose_name_plural = RECIPE_INGREDIENT_VERBOSE_NAME_PLURAL

    def __str__(self):
        return f"{self.ingredient} в {self.recipe}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=FAVORITE_FIELD_USER
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name=FAVORITE_FIELD_RECIPE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name=FAVORITE_CONSTRAINT_NAME
            )
        ]
        verbose_name = FAVORITE_VERBOSE_NAME
        verbose_name_plural = FAVORITE_VERBOSE_NAME_PLURAL

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name=CART_FIELD_USER
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='in_cart',
        verbose_name=CART_FIELD_RECIPE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name=CART_CONSTRAINT_NAME
            )
        ]
        verbose_name = CART_VERBOSE_NAME
        verbose_name_plural = CART_VERBOSE_NAME_PLURAL

    def __str__(self):
        return f"{self.user} - {self.recipe}"
