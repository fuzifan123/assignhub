from django.contrib import admin
from django.urls import path, include
from api.views import index_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', index_view, name='index'),
]