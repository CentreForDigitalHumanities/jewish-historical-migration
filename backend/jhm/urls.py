"""jewish-historical-migration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from data.views import RecordViewSet
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from rest_framework import routers

from .index import index
from .proxy_frontend import proxy_frontend

api_router = routers.DefaultRouter()  # register viewsets with this router
api_router.register(r'records', RecordViewSet)

urlpatterns = [
    path('admin', RedirectView.as_view(url='/admin/', permanent=True)),
    path('api', RedirectView.as_view(url='/api/', permanent=True)),
    path('api-auth', RedirectView.as_view(url='/api-auth/', permanent=True)),
    path('admin/', admin.site.urls),
    path('api/', include(api_router.urls)),
    path('api-auth/', include(
        'rest_framework.urls',
        namespace='rest_framework',
    )),
]

if settings.PROXY_FRONTEND:
    # Catch-all: unknown paths are handled by the proxied SPA.
    urlpatterns.append(re_path(r'^(?P<path>.*)$', proxy_frontend))
elif settings.SERVE_STATIC_FRONTEND:
    # Catch-all: unknown paths are handled by the compiled SPA.
    urlpatterns.append(re_path(r'^.*$', index))
else:
    # The backend-only application starts at Django's admin interface.
    urlpatterns.append(path('', RedirectView.as_view(url='/admin/')))
