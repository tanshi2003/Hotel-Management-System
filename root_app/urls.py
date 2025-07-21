from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name="home" ),
    path('contact', views.ContactView.as_view(), name="contact" ),
    path('about', views.AboutView.as_view(), name="about" ),
    path('search',views.SearchRoomView.as_view(), name='search'),

]