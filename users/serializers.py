from rest_framework import serializers
from .models import User
from django.contrib import  auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=60, min_length=6, write_only=True)
    
    class Meta:
        model = User
        fields = ['name','email', 'password', 'photo']
        # extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, attrs):
        email = attrs.get('email', '')
        name = attrs.get('name', '')
        
        if not name.isalnum():
            raise serializers.ValidationError('The name should only contain alphanumeric characters')
        return attrs
        
        # return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)
    
    class Meta:
        model=User
        fields=['token']

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3) # not including read_only=True makes it a required field 
    password = serializers.CharField(max_length=68, min_length=6, write_only=True) 
    # username = serializers.CharField(max_length=255, min_length=3, read_only=True)
    tokens = serializers.CharField(max_length=68, min_length=6, read_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'tokens']
    
    
    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        
        user = auth.authenticate(email=email, password=password)
        
        if not user:
            raise AuthenticationFailed('Invalid Login credentials, try again')
        
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        
    
        return {
            'email': user.email,
            'tokens': user.tokens
        }
        
        return super().validate(attrs)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    # redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']

class UpdatePasswordSerializer(serializers.Serializer):
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
        return super().validate(attrs)

