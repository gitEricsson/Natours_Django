from django.urls import path, include
from rest_framework_nested import routers
from .views import TourViewSet
from bookings.views import BookingViewSet
from reviews.views import ReviewViewSet

router = routers.DefaultRouter()
router.register(r'', TourViewSet)

tour_router = routers.NestedDefaultRouter(router, r'', lookup='tour')
tour_router.register(r'bookings', BookingViewSet, basename='tour-bookings')
tour_router.register(r'reviews', ReviewViewSet, basename='tour-reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(tour_router.urls)),
]