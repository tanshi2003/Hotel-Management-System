"""hotel_managemen_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('hms/home/', include('root_app.urls',)),
    path('hms/rooms/', include('hotel_room.urls')),
    path('hms/user/', include(('user_profile.urls', 'user_profile'))),
    path('hms/room-booking/', include('room_booking.urls')),
    path('hms/management/', include('management.urls')),
    path('/', include('root_app.urls',)),
]
