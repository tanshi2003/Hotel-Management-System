from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('root_app.urls')),  # this line handles '/'
    path('hms/home/', include('root_app.urls')),
    path('hms/rooms/', include('hotel_room.urls')),
    path('hms/user/', include(('user_profile.urls', 'user_profile'))),
    path('hms/room-booking/', include('room_booking.urls')),
    path('hms/management/', include('management.urls')),
]
