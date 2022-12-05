from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


# Create your tests here.
class LoginTestCase(APITestCase):
    login_url = reverse('rest_login')

    def setUp(self) -> None:
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


class LogoutTestCase(APITestCase):
    logout_url = reverse('rest_logout')

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='ultraman', password='ultrabrothers')
        self.client.force_authenticate(user=self.user)  # type: ignore

    def test_logout_successfully(self) -> None:
        """
        Ensure user who already login can logout successfully
        """
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_with_non_login_user(self) -> None:
        """
        Ensure user who not login cannot access logout
        """
        self.client.force_authenticate(user=None, token=None)  # type: ignore
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class HomePageTestCase(APITestCase):
    home_url = reverse('homepage')

    def setUp(self) -> None:
        pass

    def test_homepage_successfully_access(self) -> None:
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_homepage_error(self) -> None:
        response = self.client.post(self.home_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
