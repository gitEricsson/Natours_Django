from rest_framework import viewsets
from .models import Booking
from .serializers import BookingSerializer
from drf_yasg.utils import swagger_auto_schema
from .permissions import IsAdminOrLeadGuide


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = (IsAdminOrLeadGuide,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Short-circuit if Swagger is generating the schema
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        # Ensure we only return bookings for the authenticated user
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        else:
            return Booking.objects.none()


