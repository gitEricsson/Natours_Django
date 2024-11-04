from django.shortcuts import render
from rest_framework import generics, status, views, viewsets
from .serializers import SignupSerializer, EmailVerificationSerializer, LoginSerializer, ConfirmLoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, UserSerializer, UpdatePasswordSerializer, LogoutSerializer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from .models import User, Token
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from .utils import Util, AppError
from .permissions import IsAdmin, IsOwnerOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_object(self):
        return super().get_object()

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
        
        try:
            current_site = get_current_site(request).domain
            relativeLink = reverse('email-verify') # retrieve url path
            absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
            
            email_body = f"Hi {user.name}, Welcome to the Natours Family! We're thrilled you've joined us. To complete your registration, please verify your account by clicking the following link: {absurl}. If you didn't sign up for Natours, please disregard this email."
            
            email_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 5px; }}
                    h1 {{ color: #4CAF50; }}
                    .cta-button {{ display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Welcome to Natours!</h1>
                    <p>Hi {user.name},</p>
                    <p>We're thrilled to have you join the Natours family. Your adventure begins here!</p>
                    <p>To get started, please verify your account by clicking the button below:</p>
                    <p><a href="{absurl}" class="cta-button" target="_blank">Verify Your Account</a></p>
                    <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                    <p>{absurl}</p>
                    <p>If you didn't sign up for Natours, please disregard this email.</p>
                    <p>Happy exploring!</p>
                    <p>The Natours Team</p>
                </div>
            </body>
            </html>
            """
            # data={'email_body': email_body, 'to_email': user.email, 'email_subject':'Verify your email'}
            data={'email_body': email_body, 'to_email': user.email, 'email_subject':'Welcome to Natours', 'email_html': email_html}
                    
            # Util.send_email_gmail(data)
            Util.send_email_brevo(data)
            
            return Response ({'status': 'success', 'message': 'Confirmation Link sent to email!','data': user_data}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            raise AppError('There was an error sending the email. Please Try again!', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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


## For Login without confirmation
# class LoginView(generics.GenericAPIView):
#     serializer_class=LoginSerializer
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         return Response(serializer.data, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    serializer_class=LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        name = serializer.validated_data.get('name')
        login_token = serializer.validated_data.get('login_token')

        try:
            email_body = f"""
            Hi {name},

            Welcome to Natours!
            Your Confirmation Code is:

            {login_token}

            Please use this code to complete your login process.

            If you didn't request this code, please ignore this email.

            Best regards,
            The Natours Team
            """
        
            email_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 5px;">
                    <h2 style="color: #4CAF50;">Welcome to Natours!</h2>
                    <p>Hi {name},</p>
                    <p>Your Natours Confirmation Code is:</p>
                    <div style="background-color: #4CAF50; color: white; padding: 10px; text-align: center; font-size: 24px; border-radius: 3px;">
                        {login_token}
                    </div>
                    <p>Please use this code to complete your login process.</p>
                    <p style="font-style: italic; color: #777;">If you received this email without signing up, please ignore it.</p>
                    <hr style="border: none; border-top: 1px solid #ddd;">
                    <p style="font-size: 12px; color: #777;">This is an automated message, please do not reply.</p>
                </div>
            </body>
            </html>
            """
            data={'email_body': email_body, 'to_email': email, 'email_subject':'Confirm Login', 'email_html': email_html}
                    
            Util.send_email_brevo(data)
            
            return Response({
                'status': 'success',
                'message': 'Confirmation code sent to email!',
                'data': {'email': email}
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            raise AppError('There was an error sending the email. Please Try again!', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmLoginView(generics.GenericAPIView):
    serializer_class= ConfirmLoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        login_token = serializer.validated_data['login_token']

        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise AuthenticationFailed('Invalid email')

        try:
            token = Token.objects.get(user=user)
        except ObjectDoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if token.login_token != login_token:
            raise AppError('Invalid confirmation code', status_code=status.HTTP_400_BAD_REQUEST)

        # Update the token
        token.login_token = None
        token.save()
        
        # Create and send token
        return Response(serializer.data, status=status.HTTP_200_OK)


class ForgotPassword(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data['email']
        
        if User.objects.filter(email=email).exists():
            try:
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
            except Exception as e:
                raise AppError('There was an error sending the email. Please Try again!', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'failed': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


class ResetPassword(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid. Kindly request for a new token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response({'success':True, 'message':'Password reset successfully', 'uidb64': uidb64, 'token':token}, status=status.HTTP_200_OK)
        
        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Token is not valid. Kindly request for a new token'}, status=status.HTTP_401_UNAUTHORIZED)

class UpdatePasswordAPIView(generics.GenericAPIView):
    serializer_class = UpdatePasswordSerializer
    permission_classes = [IsAuthenticated,]


    def patch(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # serializer = self.serializer_class(data=request.data, context={'user': request.user})

        # Set the new password
        user = request.user
        user.set_password(serializer.validated_data['password_new'])
        user.save()
        
        return Response({'success': True, 'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = [IsAuthenticated,]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

class GetMeView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

class UpdateMeView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def patch(self, request):
        if any(key in request.data for key in ('email', 'password', 'confirm_password', 'is_staff', 'is_superuser')):            
            return Response({
        'error': 'This route is not for password updates. Please use update-password.'
        }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteMeView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def delete(self, request):
        user = request.user
        
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token=token)
        
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)