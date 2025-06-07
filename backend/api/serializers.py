from rest_framework import serializers
from djoser.serializers import (UserCreateSerializer
                                as BaseUserCreateSerializer,
                                UserSerializer as BaseUserSerializer)
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Recipe, Ingredient, RecipeIngredient)
from .constants import (
    MIN_INGREDIENT_AMOUNT, MIN_AMOUNT_INGREDIENT_ERROR,
    INVALID_CURRENT_PASSWORD_ERROR, IMAGE_REQUIRED_ERROR,
    COOKING_TIME_MIN_ERROR, EMPTY_INGREDIENTS_ERROR,
    DUPLICATE_INGREDIENTS_ERROR, MIN_COOKING_TIME
)

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'avatar', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return not user.is_anonymous and (user.subscriptions
                                          .filter(author=obj).exists())


class AvatarUploadSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'password')


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(INVALID_CURRENT_PASSWORD_ERROR)
        return value


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count',
                                             read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()

        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]

        return RecipeShortSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']
        read_only_fields = ['name', 'measurement_unit']


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True, read_only=True)
    image = serializers.ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'name', 'image', 'text',
            'cooking_time', 'ingredients',
            'is_favorited', 'is_in_shopping_cart'
        ]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and (obj.favorited_by
                                          .filter(user=user).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and (obj.in_cart
                                          .filter(user=user).exists())


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']

    def validate_amount(self, value):
        if value < MIN_INGREDIENT_AMOUNT:
            raise serializers.ValidationError(MIN_AMOUNT_INGREDIENT_ERROR)
        return value


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ['name', 'image', 'text', 'cooking_time', 'ingredients',
                  'author']

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(IMAGE_REQUIRED_ERROR)
        return value

    def validate_cooking_time(self, value):
        if value < MIN_COOKING_TIME:
            raise serializers.ValidationError(COOKING_TIME_MIN_ERROR)
        return value

    def validate(self, attrs):
        ingredients = attrs.get('ingredients')
        request = self.context.get('request')

        if request and request.method in ('POST', 'PUT', 'PATCH'):
            if ingredients is None:
                raise serializers.ValidationError({
                    'ingredients': EMPTY_INGREDIENTS_ERROR
                })
            if not ingredients:
                raise serializers.ValidationError({
                    'ingredients': EMPTY_INGREDIENTS_ERROR
                })

            seen = set()
            for ingredient in ingredients:
                ing_id = ingredient['id'].id
                if ing_id in seen:
                    raise serializers.ValidationError({
                        'ingredients': DUPLICATE_INGREDIENTS_ERROR
                    })
                seen.add(ing_id)

        return attrs

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        author = self.context['request'].user
        recipe = super().create({**validated_data, 'author': author})
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.recipe_ingredients.all().delete()
        self._save_ingredients(instance, ingredients_data)
        return instance

    def _save_ingredients(self, recipe, ingredients_data):
        ingredient_instances = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            ) for item in ingredients_data
        ]

        RecipeIngredient.objects.bulk_create(ingredient_instances)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
