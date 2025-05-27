from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet, \
    UserViewSet, SubscriptionListView
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/subscriptions/', SubscriptionListView.as_view(),
         name='subscriptions'),
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
