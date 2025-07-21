from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_GET, require_POST
import json
from datetime import date, time, datetime

from .models import Room 
from room_booking.models import Booking

# Create your views here.
class RoomsView(View):
    template_name = 'pages/rooms.html'

    def get(self, req, *args, **kwargs):
        rooms = Room.objects.all()
        context = {
            'title': 'Hotel Rooms',
            'active_nav_item': 'nav-rooms',
            'rooms':rooms

        }
        return render(req, self.template_name, context=context)

class RoomDetailsView(View):
    template_name = "pages/room_details.html"

    ROOM_STATUS = (

        ("available", "Available"),
        ("resersved", "Resersved"),
        ("occupied", "Occupied"),
        ("not available", "Not Available"),
        ("being serviced", "Being Serviced"),
        ("other", "Other")
    )

    def get(self, req, *args, **kwargs):
        room_number = req.GET.get('roomNumber', None)
        print(room_number)
        room_details = Room.objects.get(room_number=room_number)
        context={
            'title': 'Room Details',
            'active_nav_item': 'nav-rooms',
            "room_details":room_details
        }
        
        return render(req, self.template_name, context=context)
       
@require_GET
def get_standard_rooms(req):
    filtered_rooms = Room.objects.filter(style='standard').values()
    return JsonResponse({'filtered_rooms':list(filtered_rooms)})

@require_GET
def get_delux_rooms(req):
    delux_rooms = Room.objects.filter(style='delux').values()
    return JsonResponse({'filtered_rooms':list(delux_rooms)})

@require_GET
def get_family_suit(req):
    filtered_rooms = Room.objects.filter(style='family').values()
    return JsonResponse({'filtered_rooms':list(filtered_rooms)})

@require_GET
def get_business_suit(req):
    filtered_rooms = Room.objects.filter(style='business').values()
    return JsonResponse({'filtered_rooms':list(filtered_rooms)})

@require_POST
def check_room_availability(req):
    data = json.loads(req.body)
    print(data)
    checkin_datetime = datetime.strptime(data['checkInDate'], "%Y-%m-%d").date()
    checkout_datetime = datetime.strptime(data['checkOutDate'], "%Y-%m-%d").date()

    filtered_room_booking = Booking.objects.filter(room__room_number=data['roomNumber'], end_date__gt=checkin_datetime).values()
    print(filtered_room_booking)
    print(checkin_datetime)
    print(checkout_datetime)
    response = {'is_available': True}
    if filtered_room_booking:
        response["is_available"] = False

    return JsonResponse(response)

