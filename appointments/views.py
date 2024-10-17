from rest_framework import viewsets
from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        tour_id = self.kwargs.get('tour_id')
        if tour_id:
            return self.queryset.filter(tour__id=tour_id)
        return self.queryset