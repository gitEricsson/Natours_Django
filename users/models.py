from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken
import random

class UserManager(BaseUserManager):
    def create_user(self, name, email, password=None, **extra_fields):
        if not name: # same as if name is None
            raise ValueError('The Name field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, **extra_fields)
        user.set_password(password)
        # user.save(using=self._db)
        user.save()
        return user

    def create_superuser(self, name, email, password=None, **extra_fields):
        if name is None:
            raise TypeError('Please tell us your name')
        if email is None:
            raise TypeError('Please provide your email')
        if password is None:
            raise TypeError('Please provide your password')
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        user = self.create_user(name, email, password, **extra_fields)
        # user.is_superuser = True
        user.save()
        return user

AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google', 'email': 'email'}

def upload_to(instance, filename):
    # Customize the file path based on your requirements
    return f"dev-data/img/{instance.id}/{filename}"

class User(AbstractBaseUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_verified=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    role = models.CharField(default='user')
    photo = models.ImageField(upload_to=upload_to, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.email
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    login_token = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def create_login_token(self):
        self.login_token = str(random.randint(100000, 999999))
        self.save()
        return self.login_token