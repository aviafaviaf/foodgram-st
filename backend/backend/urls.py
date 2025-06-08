from django.contrib import admin
from django.urls import path, include
from api.views import RecipeShortRedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<slug:short_id>/', RecipeShortRedirectView.as_view(),
         name='recipe-short-redirect'),
]
