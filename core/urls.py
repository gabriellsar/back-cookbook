from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from app.views import RegisterView

urlpatterns = [
    path('', RedirectView.as_view(url='/api/docs/swagger/', permanent=True), name='index'),

    path('admin/', admin.site.urls),
    path('api/', include('app.urls')), 

    # Authentication endpoints
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Swagger and Redoc documentation endpoints
    path('api/schema/',SpectacularAPIView.as_view(authentication_classes=[],permission_classes=[AllowAny],),name='schema'),
    path('api/docs/swagger/',SpectacularSwaggerView.as_view(url_name='schema',authentication_classes=[],permission_classes=[AllowAny],),name='schema-swagger-ui'),
    path('api/docs/redoc/',SpectacularRedocView.as_view(url_name='schema',authentication_classes=[], permission_classes=[AllowAny],),name='schema-redoc'),
]
