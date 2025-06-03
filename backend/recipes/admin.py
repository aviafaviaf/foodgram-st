from django.contrib import admin

from .models import Recipe, Ingredient, RecipeIngredient, Favorite, \
    ShoppingCart


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    autocomplete_fields = ['ingredient']
    verbose_name = "Ингредиент"
    verbose_name_plural = "Ингредиенты"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username', 'author__email')
    inlines = [RecipeIngredientInline]
    autocomplete_fields = ['author']

    def favorites_count(self, obj):
        return obj.favorited_by.count()
    favorites_count.short_description = 'В избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    autocomplete_fields = ['recipe', 'ingredient']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    autocomplete_fields = ['user', 'recipe']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
