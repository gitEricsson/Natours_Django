from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsUser, IsUserOrAdmin
from bookings.decorators import is_booked


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # http_method_names = ['get', 'post']
    
    def get_permissions(self):
        if self.action in ['create']:
            # Only allow 'user' for these actions
            self.permission_classes = [IsAuthenticated, IsUser]
        if self.action in ['update', 'partial_update', 'destroy']:
            # Only allow 'user', 'admin' for these actions
            self.permission_classes =  [IsAuthenticated, IsUserOrAdmin]
        elif self.action in ['retrieve', 'list']:
            # Allow any authenticated user to access these actions
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    @is_booked
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        if 'user_id' in kwargs or 'tour_id' in kwargs:  # Check if it's a nested route
            return Response({"error": "Retrieve not allowed in nested routes"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().retrieve(request, *args, **kwargs)  # Allow retrieve for unnested routes
    
    def get_queryset(self):
        tour_id = self.kwargs.get('tour_id')
        user_id = self.kwargs.get('user_id')
        if tour_id:
            return Review.objects.filter(tour_id=tour_id)
        if user_id:
            return Review.objects.filter(user_id=user_id)
        return Review.objects.all()