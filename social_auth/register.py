
from django.contrib.auth import authenticate
from users.models import User
import os
import random
from rest_framework.exceptions import AuthenticationFailed


def generate_name(name):

    name = name.lower()
    if not User.objects.filter(name=name).exists():
        return name
    else:
        random_name = name + str(random.randint(0, 1000))
        return generate_name(random_name)


def register_social_user(provider, user_id, email, name):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():

        if provider == filtered_user_by_email[0].auth_provider:

            registered_user = authenticate(
                email=email, password=os.environ.get('SOCIAL_SECRET'))

            return {
                'name': registered_user.name,
                'email': registered_user.email,
                'tokens': registered_user.tokens()}

        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

    else:
        user = {
            'name': generate_name(name), 'email': email,
            'password': os.environ.get('SOCIAL_SECRET')}
        user = User.objects.create_user(**user)
        user.is_verified = True
        user.auth_provider = provider
        user.save()

        new_user = authenticate(
            email=email, password=os.environ.get('SOCIAL_SECRET'))
        return {
            'email': new_user.email,
            'name': new_user.name,
            'tokens': new_user.tokens()
        }