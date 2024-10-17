# tours/views.py
from .models import Tour
from .serializers import TourSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Min, Max, Sum
from django.db.models.functions import TruncMonth, Cast
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .permissions import IsAdminOrGuide, IsAdminOrLeadGuide
from django.db.models.functions import TruncMonth
from django.db.models import Count, F, Func, Subquery, OuterRef
from django.db.models import DateTimeField
from collections import defaultdict


class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    lookup_field = 'id'
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only allow 'admin' or 'lead-guide' for these actions
            self.permission_classes = [IsAdminOrLeadGuide,]
        elif self.action in ['retrieve', 'list']:
            # Allow any authenticated user to access these actions
            self.permission_classes = [IsAuthenticatedOrReadOnly,]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def top_5_cheap(self, request):
        try:
            tours = Tour.objects.order_by('price')[:5]
            serializer = self.get_serializer(tours, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'Error':  str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=['get'], url_path=r'monthly-plan/(?P<year>[0-9]{4})', permission_classes=[IsAdminOrGuide])
    def monthly_plan(self, request, year=None):
        try:
            monthly_data = defaultdict(int)
            
            for i in range(3):  # Assuming max 3 dates per tour
                # Subquery to get the specific date index
                sub = Tour.objects.filter(id=OuterRef('id')).annotate(
                    unnested_date=Func(F('start_dates'), function='unnest')
                ).values('unnested_date')[i:i+1]  # Get i-th date
                
                # Query tours for the specific date and count per month
                tours = Tour.objects.annotate(date=Cast(Subquery(sub), output_field=DateTimeField())).filter(
                    date__year=year
                ).annotate(month=TruncMonth('date')).values('month').annotate(
                    tour_count=Count('id', distinct=True)
                ).order_by('month')
                
                # Aggregate the results
                for tour in tours:
                    month = tour['month']
                    monthly_data[month] += tour['tour_count']  # Add count to the corresponding month

            # Convert monthly_data back to a list for the response
            compiled_results = [{'month': month, 'tour_count': count} for month, count in sorted(monthly_data.items())]

            return Response(compiled_results, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'Error':  str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=['get'], url_path=r'tour-stats')
    def tour_stats(self, request):
        try:
            stats = Tour.objects.aggregate(
                total_tours=Count('id'),
                avg_price=Avg('price'),
                min_price=Min('price'),
                max_price=Max('price'),
                total_sales=Sum('price'),
            )
            return Response(stats, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'Error':  str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path=r'tours-within/(?P<distance>\d+)/center/(?P<latlng>[-.\d,]+)/unit/(?P<unit>\w+)')
    def tours_within(self, request, distance=None, latlng=None, unit=None):
        try:
            lat, lng = map(float, latlng.split(','))
            point = Point(lng, lat, srid=4326)
            unit_conversion = {'mi': 1609.34, 'km': 1000}  # meters
            radius = float(distance) * unit_conversion.get(unit, 1)
            tours = Tour.objects.annotate(distance=Distance('start_location__geometry', point)).filter(distance__lte=radius)
            serializer = self.get_serializer(tours, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'Error':  str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

    @action(detail=False, methods=['get'], url_path=r'distances/(?P<latlng>[-.\d,]+)/unit/(?P<unit>\w+)')
    def distances(self, request, latlng=None, unit=None):
        try:
            lat, lng = map(float, latlng.split(','))
            point = Point(lng, lat, srid=4326)
            unit_conversion = {'mi': 1609.34, 'km': 1000}  # meters
            multiplier = unit_conversion.get(unit, 1)
            tours = Tour.objects.annotate(distance=Distance('start_location__geometry', point) / multiplier).order_by('distance')
            distances = tours.values('id', 'name', 'distance')
            
            return Response(distances, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'Error':  str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
