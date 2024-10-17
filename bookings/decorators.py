from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from .models import Booking

def is_booked(func):
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            raise PermissionDenied("You need to be logged in to perform this action.")

        user = request.user
        tour_id = kwargs.get('tour_pk')

        if not Booking.objects.filter(user=user,tour_id=tour_id).exists():
            raise PermissionDenied("You cannot review a tour you haven't booked.")
        return func(request, *args, **kwargs)
        
    return wrapper