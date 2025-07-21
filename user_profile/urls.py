from django.urls import path

from user_profile import views

urlpatterns = [
    path("registration/", views.RegisterView.as_view(), name='registration' ),
    path("login/", views.LoginView.as_view(), name='login' ),
    path("logout/", views.LogoutView.as_view(), name='logout' ),
    path("profile/", views.ProfileView.as_view(), name='profile' ),

]