from rest_framework.test import APITestCase
from django.urls import reverse

class TestSetUp(APITestCase):
    
    def setUp(self):
        self.signup_url=reverse('signup')
        self.login_url = reverse('login')
        
        self.user_data = {
            'email': "email@gmail.com",
            'name': "email",
            'password': "email@gmail.com",
        }
        
        return super().setUp()
    
    def tearDown(self):
        return super().tearDown()