from rest_framework import serializers
from .models import User, Token
from django.contrib import  auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=60, min_length=6, write_only=True)
    
    class Meta:
        model = User
        fields = ['name','email', 'password', 'photo']
        # extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, attrs):
        email = attrs.get('email', '')
        name = attrs.get('name', '')
        
        if not name.replace(" ", "").isalnum():
            raise serializers.ValidationError('The name should only contain alphanumeric characters')
        return attrs
        
        # return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)
    
    class Meta:
        model = User
        fields = ['token']


## For Login without confirmation
# class LoginSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(max_length=255, min_length=3) # not including read_only=True makes it a required field 
#     password = serializers.CharField(max_length=68, min_length=6, write_only=True) 
#     tokens = serializers.SerializerMethodField()

#     def get_tokens(self, obj):
#         user = User.objects.get(email=obj['email'])

#         return {
#             'refresh': user.tokens()['refresh'],
#             'access': user.tokens()['access']
#         } # user.tokens()['access'] is same as user.tokens.get('access')
    
#     class Meta:
#         model = User
#         fields = ['email', 'password', 'tokens']
    
    
#     def validate(self, attrs):
#         email = attrs.get('email', '')
#         password = attrs.get('password', '')
        
#         user = auth.authenticate(email=email, password=password)
        
#         if not user:
#             raise AuthenticationFailed('Invalid Login credentials, try again')
        
#         if not user.is_active:
#             raise AuthenticationFailed('Account disabled, contact admin')
        
#         if not user.is_verified:
#             raise AuthenticationFailed('Email is not verified')
        
    
#         return {
#             'email': user.email,
#             'tokens': user.tokens
#         }

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100, min_length=3) # not including read_only=True makes it a required field 
    password = serializers.CharField(max_length=20, min_length=6, write_only=True) 

    class Meta:
        model = User
        fields = ['email', 'password']
    
    
    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
                
        user = auth.authenticate(email=email, password=password)
        
        if not user:
            raise AuthenticationFailed('Invalid Login credentials, try again', 401)
        
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin', 400)
        
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified', 400)
        
        token, _ = Token.objects.get_or_create(user=user)
        login_token = token.create_login_token()
        
        return {
            'email': user.email,
            'name': user.name,
            'login_token': login_token
        }

class ConfirmLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    login_token = serializers.CharField(max_length=6, min_length=6, write_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        } # user.tokens()['access'] is same as user.tokens.get('access')
    

    def validate_login_token(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Confirmation code must be numeric.")
        return value



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)

class UpdatePasswordSerializer(serializers.Serializer):
    password_current = serializers.CharField(
        min_length=6, max_length=68, write_only=True, required=True)
    password_new = serializers.CharField(
        min_length=6, max_length=68, write_only=True, required=True)
    password_new_confirm = serializers.CharField(
        min_length=6, max_length=68, write_only=True, required=True)

    class Meta:
        fields = ['passwordCurrent', 'passwordNew', 'passwordNewConfirm']
    
    ## would work if we were validating only one field called password_current
    # def validate_password_current(self, value):
    #     user = self.context['request'].user
    #     if not user.check_password(value):
    #         raise serializers.ValidationError("Current password is incorrect")
    #     return value
    
    def validate(self, attrs):
            user = self.context['request'].user

            # Validate current password
            if not check_password(attrs['password_current'], user.password):
                raise serializers.ValidationError({"password_current": "Current password is incorrect."})

            # Validate new password confirmation
            if attrs['password_new'] != attrs['password_new_confirm']:
                raise serializers.ValidationError({"password_new_confirm": "New passwords do not match."})
            
            return attrs

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')

