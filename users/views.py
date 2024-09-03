# # from rest_framework import viewsets, generics, permissions
# # from .models import User
# # from .serializers import UserSerializer

# # from rest_framework.authtoken.serializers import AuthTokenSerializer
# # from rest_framework.response import Response
# # from django.contrib.auth import login

# # class UserViewSet(viewsets.ModelViewSet):
# #     queryset = User.objects.all()
# #     serializer_class = UserSerializer

# # class LoginAPI(KnoxLoginView):
# #     permission_classes = (permissions.AllowAny,)

# #     def post(self, request, format=None):
# #         serializer = AuthTokenSerializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         user = serializer.validated_data['user']
# #         login(request, user)
# #         return Response({
# #             "user": UserSerializer(user).data,
# #             "token": AuthToken.objects.create(user)[1]
# #         })




# from rest_framework import viewsets
# from .models import User
# from .serializers import UserSerializer
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.authtoken.serializers import AuthTokenSerializer
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny
# from rest_framework import status
# from rest_framework.parsers import MultiPartParser, FormParser

# from rest_framework import viewsets
# from rest_framework.decorators import action
# from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import send_mail

# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAuthenticated]
#     parser_classes = (MultiPartParser, FormParser)

#     @action(detail=False, methods=['post'])
#     def signup(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         token = default_token_generator.make_token(user)
#         send_mail(
#             'Confirm your email',
#             f'Use this token to confirm your email: {token}',
#             'from@example.com',
#             [user.email],
#         )
#         return Response(serializer.data)

#     @action(detail=False, methods=['post'])
#     def confirm_signup(self, request):
#         token = request.data.get('token')
#         user = User.objects.get(email=request.data.get('email'))
#         if default_token_generator.check_token(user, token):
#             user.email_confirmed = True
#             user.save()
#             return Response({'status': 'Email confirmed'})
#         return Response({'status': 'Invalid token'}, status=400)


    
# class SignupView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             token = AuthToken.objects.create(user)[1]
#             return Response({
#                 "user": UserSerializer(user).data,
#                 "token": token
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = AuthTokenSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             user = serializer.validated_data['user']
#             token = AuthToken.objects.create(user)[1]
#             return Response({
#                 "user": UserSerializer(user).data,
#                 "token": token
#             })
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         request.user.auth_token.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


from django.shortcuts import render
from rest_framework import generics, status, views
from .serializers import SignupSerializer, EmailVerificationSerializer, LoginSerializer, ForgotPasswordSerializer, UpdatePasswordSerializer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect
import os




class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']

class SignupView(generics.GenericAPIView):
    serializer_class = SignupSerializer
    parser_classes = (MultiPartParser, FormParser)
    renderer_classes = (UserRenderer,)

    
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
                
        token = RefreshToken.for_user(user).access_token
                
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify') # retrieve url path
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        
        email_body = f"Hi {user.name}, Welcome to the Family. We're happy you signed up for Natours. \n Kindly visit this Link to verify your account: {absurl}. \n If you received this mail without signing up, please ignore it!`"
                
        data={'email_body': email_body, 'to_email': user.email, 'email_subject':'Verify your email'}
                
        # Util.send_email_gmail(data)
        Util.send_email_brevo(data)
        
        return Response (user_data, status=status.HTTP_201_CREATED)
    
class VerifyEmail(views.APIView):
    serializer_class=EmailVerificationSerializer
    

    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
    
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload['user_id'])
            
            if not user.is_verified:
                user.is_verified = True
                user.save()
            
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Link Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(generics.GenericAPIView):
    serializer_class=LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class ForgotPassword(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data['email']
        
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + absurl
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Passsword Reset'}
            
            Util.send_email_brevo(data)

        
            return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        
        return Response({'failed': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


class ResetPassword(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid. Kindly request for a new token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response({'success':True, 'message':'Credentials Validated', 'uidb64': uidb64, 'token':token}, status=status.HTTP_200_OK)
        
        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Token is not valid. Kindly request for a new token'}, status=status.HTTP_401_UNAUTHORIZED)

class UpdatePasswordAPIView(generics.GenericAPIView):
    serializer_class = UpdatePasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)