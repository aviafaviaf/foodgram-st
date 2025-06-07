from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404

from users.models import Subscription
from recipes.models import Recipe, ShoppingCart, Favorite, Ingredient
from .serializers import (RecipeReadSerializer, RecipeWriteSerializer,
                          RecipeShortSerializer, IngredientSerializer,
                          AvatarUploadSerializer, SubscriptionSerializer,
                          SetPasswordSerializer)
from .permissions import IsAuthorOrReadOnly
from .filters import RecipeFilter, IngredientFilter

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
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

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response({'errors': 'Уже в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe,
                                               context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            cart_item = (ShoppingCart.objects
                         .filter(user=user, recipe=recipe).first())
            if not cart_item:
                return Response({'errors': 'Этого рецепта не было в списке'},
                                status=status.HTTP_400_BAD_REQUEST)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user

        ingredients = (
            Ingredient.objects
            .filter(recipes__in_cart__user=user)
            .annotate(
                total_amount=Sum('recipeingredient__amount'),
                unit=F('measurement_unit')
            )
            .values('name', 'unit', 'total_amount')
            .order_by('name')
        )

        lines = ['Список покупок:\n']
        for item in ingredients:
            lines.append(
                f"{item['name']} – {item['total_amount']} {item['unit']}")

        content = '\n'.join(lines)
        filename = 'shopping_list.txt'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=['post', 'delete'], url_path='favorite',
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response({'errors': 'Уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe,
                                               context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = (Favorite.objects
                        .filter(user=user, recipe=recipe).first())
            if not favorite:
                return Response({'errors': 'Этого рецепта нет в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)

            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeShortLinkView(APIView):
    def get(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        short_link = f"https://foodgram.example.org/s/{recipe.id:03x}"
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class UserViewSet(DjoserUserViewSet):

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar',
            permission_classes=[permissions.IsAuthenticated])
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarUploadSerializer(instance=request.user,
                                                data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'avatar': request.user.avatar.url},
                            status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            request.user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user,
                                         context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='set_password',
            permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe',
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = self.get_object()

        if user == author:
            return Response({'errors': 'Нельзя подписаться на самого себя.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(author,
                                                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(user=user,
                                                       author=author).first()
            if not subscription:
                return Response(
                    {'errors': 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST)

            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='subscriptions')
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(page,
                                                many=True,
                                                context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(queryset,
                                            many=True,
                                            context={'request': request})
        return Response(serializer.data)
