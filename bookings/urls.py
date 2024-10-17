from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, CheckoutSessionView, BookingCheckoutView

router = DefaultRouter()
router.register(r'', BookingViewSet)

urlpatterns = [
        path('checkout-session/<int:tour_id>/', CheckoutSessionView.as_view(), name='checkout-session'),
        path('', include(router.urls)),
        path('confirmBooking/', BookingCheckoutView.as_view(), name='confirm-booking'),
]