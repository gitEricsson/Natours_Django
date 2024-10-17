import json
import requests
from rest_framework import viewsets, status
from .models import Booking
from tours.models import Tour
from appointments.models import Appointment
from appointments.decorators import is_sold_out, update_participants, get_appointment_id
from django.conf import settings
from .serializers import BookingSerializer
from drf_yasg.utils import swagger_auto_schema
from .permissions import IsAdminOrLeadGuide
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import time

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()



class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated, IsAdminOrLeadGuide)
    # http_method_names = ['get', 'post']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    # # If we wanted to prevent nested get routes
    # def retrieve(self, request, *args, **kwargs):
    #     if 'user_id' in kwargs or 'tour_id' in kwargs:  # Check if it's a nested route
    #         return Response({"error": "Retrieve not allowed in nested routes"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     return super().retrieve(request, *args, **kwargs)  # Allow retrieve for unnested routes

    @is_sold_out
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        appointment_id = response.data['appointment']
        
        update_participants(appointment_id)
        return response

    @get_appointment_id
    def destroy(self, request, *args, **kwargs):
        appointment_id = request.data['appointment']
        
        update_participants(appointment_id)
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        # Short-circuit if Swagger is generating the schema
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        
        tour_id = self.kwargs.get('tour_id')
        user_id = self.kwargs.get('user_id')
        if tour_id:
            return Booking.objects.filter(tour_id=tour_id)
        if user_id:
            return Booking.objects.filter(user_id=user_id)
        return Booking.objects.all()

class BookingCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ref = request.query_params.get('tx_ref').split('-')
        user_id, tour_id, appointment_id = ref[0], ref[1], ref[2]

        try:
            tour = Tour.objects.get(id=tour_id)
            price = tour.price

            Booking.objects.create(
                user_id=user_id,
                tour_id=tour_id,
                appointment_id=appointment_id,
                price=price
            )
            
            update_participants(appointment_id)

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Tour.DoesNotExist:
            return Response({'error': 'Tour not found'}, status=status.HTTP_404_NOT_FOUND)

class CheckoutSessionView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, tour_id):
        tour = Tour.objects.get(id=tour_id)
        if not tour:
            return Response({'error': 'Tour not found'}, status=status.HTTP_404_NOT_FOUND)

        appointment_id = request.data.get('appointment')
        
        if not appointment_id:
            return Response({'error': 'Kindly select an appointment date'}, status=status.HTTP_400_BAD_REQUEST)
        
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Prepare checkout session data
        tx_ref = f'{request.user.id}-{tour.id}-{appointment.id}-{int(time.time())}'
        payload = {
            'tx_ref': tx_ref,
            'amount': float(tour.price) * 100,
            'currency': 'NGN',
            'redirect_url': 'https://natours-6ybv.onrender.com/confirmBooking',
            'meta': {'consumer_id': tour.id},
            'customer': {'email': request.user.email, 'name': request.user.name},
            'customizations': {
                'title': f'{tour.name} Tour',
                'logo': f'https://www.natours.dev/img/tours/{tour.image_cover}',
                'description': tour.summary
            }
        }
        
        FLUTTER_SECRET_KEY = os.environ.get("FLUTTER_SECRET_KEY")

        response = requests.post(
            'https://api.flutterwave.com/v3/payments',
            json=payload,
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {FLUTTER_SECRET_KEY}'}
        )

        if response.status_code == 200:
            return Response(response.json(), status=response.status_code)
        else:
            return Response({"error": response.text}, status=response.status_code)

