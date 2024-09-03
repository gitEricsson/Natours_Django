# tours/views.py
from .models import Tour
from .serializers import TourSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from django.db.models import Avg, Count, Min, Max, Sum
from django.db.models.functions import TruncMonth
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .permissions import IsAdminOrGuide, IsAdminOrLeadGuide


class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only allow 'admin' or 'lead-guide' for these actions
            self.permission_classes = [IsAdminOrLeadGuide]
        elif self.action in ['retrieve', 'list']:
            # Allow any authenticated user to access these actions
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def top_5_cheap(self, request):
        tours = Tour.objects.order_by('price')[:5]
        serializer = self.get_serializer(tours, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'monthly-plan/(?P<year>[0-9]{4})', permission_classes=[IsAdminOrGuide])
    def monthly_plan(self, request, year=None):
        tours = Tour.objects.filter(startDates__year=year).annotate(month=TruncMonth('startDates')).values('month').annotate(tour_count=Count('id')).values('month', 'tour_count')
        return Response(tours, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'tour-stats')
    def tour_stats(self, request):
        stats = Tour.objects.aggregate(
            total_tours=Count('id'),
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
            total_sales=Sum('price'),
        )
        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'tours-within/(?P<distance>\d+)/center/(?P<latlng>[-\d,]+)/unit/(?P<unit>\w+)')
    def tours_within(self, request, distance=None, latlng=None, unit=None):
        lat, lng = map(float, latlng.split(','))
        point = Point(lng, lat)
        unit_conversion = {'mi': 1609.34, 'km': 1000}  # meters
        radius = float(distance) * unit_conversion.get(unit, 1)
        tours = Tour.objects.annotate(distance=Distance('location', point)).filter(distance__lte=radius)
        serializer = self.get_serializer(tours, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'distances/(?P<latlng>[-\d,]+)/unit/(?P<unit>\w+)')
    def distances(self, request, latlng=None, unit=None):
        lat, lng = map(float, latlng.split(','))
        point = Point(lng, lat)
        unit_conversion = {'mi': 1609.34, 'km': 1000}  # meters
        multiplier = unit_conversion.get(unit, 1)
        tours = Tour.objects.annotate(distance=Distance('location', point) / multiplier).order_by('distance')
        distances = tours.values('id', 'name', 'distance')
        return Response(distances, status=status.HTTP_200_OK)