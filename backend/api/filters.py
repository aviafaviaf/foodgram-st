import django_filters
from django_filters import rest_framework as filters

from ..recipes.models import Recipe, Ingredient


def coerce_to_bool(value):
    return value == '1'


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.TypedChoiceFilter(
        choices=(('1', 'Да'), ('0', 'Нет')),
        coerce=coerce_to_bool,
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.TypedChoiceFilter(
        choices=(('1', 'Да'), ('0', 'Нет')),
        coerce=coerce_to_bool,
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorited_by__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(in_cart__user=user)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
