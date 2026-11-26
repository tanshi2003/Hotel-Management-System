from django.urls import path

from management import views

urlpatterns = [
    path('', views.ManagementView.as_view(), name='management'),
    path('booking/<str:reservation_number>/status/', views.BookingStatusTransitionView.as_view(), name='booking_status_transition'),
]
