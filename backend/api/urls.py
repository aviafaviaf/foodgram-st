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
    path('recipes/<int:id>/get-link/', RecipeShortLinkView.as_view(),
         name='recipe-short-link'),
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
