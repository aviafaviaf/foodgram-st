from rest_framework import viewsets, permissions, filters
from recipes.models import Recipe, ShoppingCart, Favorite, Ingredient
from recipes.serializers import RecipeReadSerializer, RecipeWriteSerializer, \
    RecipeShortSerializer, IngredientSerializer
from .permissions import IsAuthorOrReadOnly
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import RecipeFilter, IngredientFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, generics
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from users.serializers import AvatarUploadSerializer, SubscriptionSerializer, \
    SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from users.models import Subscription

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = RecipeFilter
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        instance = self.get_object()
        url = f"{request.get_host()}/s/{instance.id}"
        return Response(data={"short-link": url})

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response({'errors': 'Уже в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST)

        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe,
                                           context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_from_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        cart_item = ShoppingCart.objects.\
            filter(user=user, recipe=recipe).first()
        if not cart_item:
            return Response({'errors': 'Этого рецепта не было в списке'},
                            status=status.HTTP_400_BAD_REQUEST)

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipe.objects.filter(in_cart__user=user)
        ingredients = {}

        for recipe in recipes:
            for ri in recipe.recipe_ingredients.all():
                name = ri.ingredient.name
                unit = ri.ingredient.measurement_unit
                amount = ri.amount

                if name in ingredients:
                    ingredients[name]['amount'] += amount
                else:
                    ingredients[name] = {'amount': amount, 'unit': unit}

        lines = ['Список покупок:\n']
        for name, data in ingredients.items():
            lines.append(f"{name} – {data['amount']} {data['unit']}")

        content = '\n'.join(lines)
        filename = 'shopping_list.txt'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response({'errors': 'Уже в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

        Favorite.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe,
                                           context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        favorite = Favorite.objects.filter(user=user, recipe=recipe).first()
        if not favorite:
            return Response({'errors': 'Этого рецепта нет в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class UserViewSet(DjoserUserViewSet):
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['put'], url_path='me/avatar',
            permission_classes=[IsAuthenticated])
    def set_avatar(self, request):
        serializer = AvatarUploadSerializer(instance=request.user,
                                            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'avatar': request.user.avatar.url},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='me/avatar',
            permission_classes=[IsAuthenticated])
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user,
                                         context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='set_password',
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = self.get_object()
        if user == author:
            return Response({'errors': 'Нельзя подписаться на самого себя.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(author,
                                            context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        user = request.user
        author = self.get_object()
        subscription = Subscription.objects.filter(user=user, author=author)\
            .first()
        if not subscription:
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(subscribers__user=self.request.user)
