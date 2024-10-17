
# # from rest_framework.routers import DefaultRouter


# # from .views import SignupView, LoginView, LogoutView
# from rest_framework.routers import DefaultRouter
# # from .views import UserViewSet

# router = DefaultRouter()
# # router.register(r'users', UserViewSet)

# urlpatterns = [
#     # path('signup/', SignupView.as_view(), name='signup'),
#     # path('login/', LoginView.as_view(), name='login'),
#     # path('logout/', LogoutView.as_view(), name='logout'),
# ]

from django.urls import path, include
from .views import SignupView, VerifyEmail, LoginView, ForgotPassword, ResetPassword, UpdatePasswordAPIView, UserViewSet, LogoutView, ConfirmLoginView, GetMeView, UpdateMeView, DeleteMeView
from rest_framework_simplejwt.views import (TokenRefreshView)
from rest_framework_nested import routers
from bookings.views import BookingViewSet
from reviews.views import ReviewViewSet

router = routers.DefaultRouter()
router.register(r'', UserViewSet)

user_router = routers.NestedDefaultRouter(router, r'', lookup='user')
user_router.register(r'bookings', BookingViewSet, basename='user-bookings')
user_router.register(r'reviews', ReviewViewSet, basename='user-reviews')

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('confirm-login/', ConfirmLoginView.as_view(), name='confirm-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('email-verify/', VerifyEmail.as_view(), name='email-verify'),
    path('forgot-password/', ForgotPassword.as_view(), name="forgot-password"),
    path('reset-password/<uidb64>/<token>/', ResetPassword.as_view(), name='password-reset-confirm'),
    path('update-password', UpdatePasswordAPIView.as_view(), name='update-password'),
    path('me/', GetMeView.as_view(), name='get_me'),
    path('delete-me/', DeleteMeView.as_view(), name='delete_me'),
    path('update-me/', UpdateMeView.as_view(), name='update_me'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('', include(user_router.urls)),
]