from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from si_mbe.models import Sparepart, Role, Extend_user


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
        self.assertEqual(user.username, 'kamenrider')

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
        self.client.force_authenticate(user=self.user)

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
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class HomePageTestCase(APITestCase):
    home_url = reverse('homepage')

    def setUp(self) -> None:
        pass

    def test_homepage_successfully_accessed(self) -> None:
        """
        Ensure homepage can be access
        """
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_homepage_error(self) -> None:
        """
        Ensure user who trying access homepage with wrong method got an error
        """
        response = self.client.post(self.home_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class SparepartSearchTestCase(APITestCase):

    def setUp(self) -> None:
        self.name = 'aki 1000CC'
        self.partnumber = 'AB17623-ha2092d'

        Sparepart.objects.create(
            name=self.name,
            partnumber=self.partnumber,
            quantity=50,
            motor_type='Yamaha Nmax',
            sparepart_type='24Q-22',
            price=5400000,
            grosir_price=5300000,
            brand_id=None
        )

    def test_searching_sparepart_successfully_with_result(self) -> None:
        """
        Ensure user who searching sparepart with correct keyword get correct result
        """
        response = self.client.get(reverse('search_sparepart') + f'?q={self.name}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['results'][0]['partnumber'], self.partnumber)
        self.assertEqual(response.data['message'], 'Pencarian sparepart berhasil')

    def test_searching_sparepart_without_result(self) -> None:
        """
        Ensure user who searching sparepart that doesn't exist get empty result
        """
        response = self.client.get(reverse('search_sparepart') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 0)
        self.assertEqual(response.data['message'], 'Sparepart yang dicari tidak ditemukan')


class DashboardTestCase(APITestCase):
    dashboard_url = reverse('dashboard')

    def setUp(self) -> None:
        self.role = Role.objects.create(name='Admin')
        self.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        self.extend_user = Extend_user.objects.create(user=self.user, role_id=self.role)
        self.client.force_authenticate(user=self.user)

        self.nonadmin_role = Role.objects.create(name='Karyawan')
        self.nonadmin_user = User.objects.create_user(username='Phalanx', password='TryintoTakeOver')
        self.extend_user = Extend_user.objects.create(user=self.nonadmin_user, role_id=self.nonadmin_role)

    def test_admin_dashboard_successfully_accessed(self) -> None:
        """
        Ensure user can access admin dashboard
        """
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nonlogin_user_cannot_access_admin_dashboard(self) -> None:
        """
        Ensure user who not login cannot access admin dashboard
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_user_without_admin_role_cannot_access_admin_dashboard(self) -> None:
        """
        Ensure user who already login but isn't an admin cannot access admin dashboard
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Akses ditolak')
