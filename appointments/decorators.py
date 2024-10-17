from rest_framework import status
from rest_framework.response import Response
from bookings.models import Booking
from .models import Appointment


def is_sold_out(func):
    def wrapper(request, *args, **kwargs):
        appointment_id = request.data.get('appointment')
        appointment = Appointment.objects.get(id=appointment_id)

        if appointment.sold_out:
            return Response({'error': 'Appointment is soldout'}, status=status.HTTP_400_BAD_REQUEST)

        return func(request, *args, **kwargs)
        
    return wrapper

def update_participants(appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    bookings_count = Booking.objects.filter(appointment=appointment).count()

    if bookings_count >= appointment.tour.max_group_size:
        appointment.sold_out = True
    appointment.participants = bookings_count
    appointment.save()

def get_appointment_id(func):
    def wrapper(request, *args, **kwargs):
        booking_id = kwargs.get('id')
        booking = Booking.objects.get(id=booking_id)

        request.data['appointment'] = booking.appointment.id
        request.data['tour'] = booking.tour.id
        
        return func(request, *args, **kwargs)

