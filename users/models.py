from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken

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
        
        user = self.create_user(name, email, password, **extra_fields)
        user.is_superuser = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_verified=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(default='user')
    photo = models.ImageField(upload_to='users/', null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return {self.name, self.email, self.role, self.is_active, self.photo}
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    
    # groups = models.ManyToManyField(
    #     'auth.Group',
    #     related_name='custom_user_set',  # Add this line
    #     blank=True,
    #     help_text='The groups this user belongs to.',
    #     related_query_name='custom_user'
    # )
    # user_permissions = models.ManyToManyField(
    #     'auth.Permission',
    #     related_name='custom_user_set',  # Add this line
    #     blank=True,
    #     help_text='Specific permissions for this user.',
    #     related_query_name='custom_user'
    # )

