from rest_framework.routers import DefaultRouter
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from .views import (RecipeViewSet, IngredientViewSet,
                    UserViewSet, RecipeShortLinkView)

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('recipes/<int:id>/get-link/', RecipeShortLinkView.as_view(),
         name='recipe-short-link'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
