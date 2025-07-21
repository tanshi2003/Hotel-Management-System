from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.RoomsView.as_view(), name="rooms" ),
    path('standard/', views.get_standard_rooms, name='standard_rooms'),
    path('details/', views.RoomDetailsView.as_view(), name="room_details"),
    path('details/availability', views.check_room_availability, name="room_availability"),
    path('delux/', views.get_delux_rooms, name='delux_rooms'),
    path('family/', views.get_family_suit, name='family_suit'),
    path('business/', views.get_business_suit, name='business_suit'),
]