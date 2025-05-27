from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    cooking_time = models.PositiveIntegerField(help_text='Время в минутах')
    ingredients = models.ManyToManyField('Ingredient',
                                         through='RecipeIngredient',
                                         related_name='recipes')
    short_code = models.CharField(max_length=10, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = uuid.uuid4().hex[:6]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    measurement_unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('recipe', 'ingredient')


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user} {self.recipe}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='in_cart')

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user} {self.recipe}"
