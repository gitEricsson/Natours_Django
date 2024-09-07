
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
from .views import SignupView, VerifyEmail, LoginView, ForgotPassword, ResetPassword, UpdatePasswordAPIView, UserViewSet, LogoutView
from rest_framework_simplejwt.views import (TokenRefreshView)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('email-verify/', VerifyEmail.as_view(), name='email-verify'),
    path('forgot-password/', ForgotPassword.as_view(), name="forgot-password"),
    path('reset-password/<uidb64>/<token>/', ResetPassword.as_view(), name='password-reset-confirm'),
    path('update-password', UpdatePasswordAPIView.as_view(), name='update-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]