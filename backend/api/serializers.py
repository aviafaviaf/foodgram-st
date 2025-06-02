import base64
import uuid

from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import (UserCreateSerializer
                                as BaseUserCreateSerializer,
                                UserSerializer as BaseUserSerializer)
from django.core.files.base import ContentFile
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

from recipes.models import (Recipe, Ingredient, RecipeIngredient,
                            Favorite, ShoppingCart)

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'avatar', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriptions.filter(author=obj).exists()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
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

    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.all()
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class IngredientAmountSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.DecimalField(max_digits=6, decimal_places=2)


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'name', 'image', 'text', 'cooking_time', 'ingredients'
        ]

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Изображение обязательно.')
        return value

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.')

        seen = set()
        for ingredient in ingredients:
            ing_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if ing_id in seen:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.')
            seen.add(ing_id)
            if amount is None or float(amount) < 1:
                raise serializers.ValidationError(
                    f'Количество ингредиента (id={ing_id}) \
должно быть не меньше 1.')
        return ingredients

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.recipe_ingredients.all().delete()
        self._save_ingredients(instance, ingredients_data)
        return instance

    def _save_ingredients(self, recipe, ingredients_data):
        for item in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            )

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


class Base64AvatarField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            img_data = base64.b64decode(imgstr)
            file_name = f'{uuid.uuid4()}.{ext}'
            data = ContentFile(img_data, name=file_name)
        return super().to_internal_value(data)


class AvatarUploadSerializer(serializers.ModelSerializer):
    avatar = Base64AvatarField(required=True)

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
    new_password = serializers.CharField(write_only=True, required=True,
                                         validators=[validate_password])

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль.")
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscriptions.filter(author=obj).exists()

    def get_recipes(self, obj):
        from backend.api.serializers import RecipeShortSerializer

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

    def get_recipes_count(self, obj):
        return obj.recipes.count()
