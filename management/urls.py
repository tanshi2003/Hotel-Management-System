from django.urls import path

from management import views


urlpatterns = [
    path('', views.ManagementView.as_view(), name='management')
]