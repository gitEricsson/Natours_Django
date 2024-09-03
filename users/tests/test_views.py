from .test_setup import TestSetUp
from ..models import User


class TestViews(TestSetUp):
    def test_user_can_signup(self):
        res = self.client.post(self.signup_url, self.user_data, format="multipart")
        self.assertEqual(res.data['email'], self.user_data['email'])
        self.assertEqual(res.data['name'], self.user_data['name'])
        self.assertEqual(res.status_code, 201)
        
        
    def test_user_cannot_signup_with_no_data(self):
        res = self.client.post(self.signup_url)
        self.assertEqual(res.status_code, 400)
        
    def test_user_cannot_login_with_unverified_email(self):
        self.client.post(
            self.signup_url, self.user_data, format="multipart")
        res = self.client.post(self.login_url, self.user_data, format="json")
        self.assertEqual(res.status_code, 401)

    def test_user_can_login_after_verification(self):
        response = self.client.post(
            self.signup_url, self.user_data, format="multipart")
        email = response.data['email']
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()
        res = self.client.post(self.login_url, self.user_data, format="json")
        self.assertEqual(res.status_code, 200)