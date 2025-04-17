from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('who/', include('users.urls')),
    path('who/api-auth/', include('rest_framework.urls')),
    path('who/rest-auth/', include('rest_auth.urls')),
    path('who/rest-auth/registration', include('rest_auth.registration.urls')),
    path('who/admin/', admin.site.urls),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)