from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('exploration.urls'), name='exploration'),
    path('', include('main.urls'), name='main'),
    path('member/', include('member.urls'), name='member'),
    path('', include('users.urls'), name='users'),
]
