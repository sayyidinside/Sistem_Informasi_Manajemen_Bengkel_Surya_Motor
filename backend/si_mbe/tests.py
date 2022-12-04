from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


# Create your tests here.
class LoginTestCase(APITestCase):
    def setUp(self) -> None:
        self.login_url = reverse('rest_login')

        self.data = {
            'username': 'kamenrider',
            'password': 'asasd'
        }
        self.user = User.objects.create_user(
            username=self.data['username'],
            password=self.data['password']
        )

    def test_login_successfully(self) -> None:
        """
        Ensure user with correct data can login
        """
        response = self.client.post(self.login_url, self.data)
        user = response.wsgi_request.user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.username, 'kamenrider')  # type: ignore

    def test_login_with_empty_data(self) -> None:
        """
        Ensure user that input empty data get error to fill the data
        """
        self.empty_data = {}
        response = self.client.post(self.login_url, self.empty_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_wrong_data(self) -> None:
        """
        Ensure user that input wrong data get error
        """
        self.wrong_data = {
            'username': 'daishocker',
            'password': 'asasd'
        }
        response = self.client.post(self.login_url, self.wrong_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_incomplete_data(self) -> None:
        """
        Ensure user that input incomplete data get error
        """
        self.incomplete_data = {'password': 'asdasd'}
        response = self.client.post(self.login_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
