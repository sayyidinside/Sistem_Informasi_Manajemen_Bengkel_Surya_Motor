from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.test import APITestCase
from si_mbe.models import Brand, Category, Profile, Sparepart


class SetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and non-admin user
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Profile.objects.create(user_id=cls.user, role='A', name='Richard Rider')

        cls.owner = User.objects.create_user(username='oneaboveall', password='TrueComicBookWriter')
        Profile.objects.create(user_id=cls.owner, role='P', name='One Above All')

        return super().setUpTestData()


class LoginTestCase(APITestCase):
    login_url = reverse('rest_login')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.data = {
            'username': 'kamenrider',
            'password': 'asasd'
        }
        cls.user = User.objects.create_user(
            username=cls.data['username'],
            password=cls.data['password']
        )

        return super().setUpTestData()

    def test_successfully_login(self) -> None:
        """
        Ensure user with correct data can login
        """
        response = self.client.post(self.login_url, self.data)
        user = response.wsgi_request.user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.username, 'kamenrider')

    def test_failed_to_login_with_empty_data(self) -> None:
        """
        Ensure user that input empty data get error to fill the data
        """
        response = self.client.post(self.login_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failed_to_login_with_wrong_data(self) -> None:
        """
        Ensure user that input wrong data get error
        """
        self.wrong_data = {
            'username': 'daishocker',
            'password': 'asasd'
        }
        response = self.client.post(self.login_url, self.wrong_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failed_to_login_with_incomplete_data(self) -> None:
        """
        Ensure user that input incomplete data get error
        """
        self.incomplete_data = {'password': 'asdasd'}
        response = self.client.post(self.login_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTestCase(APITestCase):
    logout_url = reverse('rest_logout')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(username='ultraman', password='ultrabrothers')

        return super().setUpTestData()

    def test_login_user_successfully_logout(self) -> None:
        """
        Ensure user who already login can logout successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nonlogin_user_failed_to_logout(self) -> None:
        """
        Ensure user who not login cannot access logout
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HomePageTestCase(APITestCase):
    home_url = reverse('homepage')

    def setUp(self) -> None:
        pass

    def test_successfully_accessed_homepage(self) -> None:
        """
        Ensure homepage can be access
        """
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_failed_to_access_homepage_with_wrong_method(self) -> None:
        """
        Ensure user who trying access homepage with wrong method got an error
        """
        response = self.client.post(self.home_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class SparepartSearchTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up brand data
        cls.brand_1 = Brand.objects.create(name='Taldore')
        cls.brand_2 = Brand.objects.create(name='wildmount')

        # Setting up category data
        cls.category_1 = Category.objects.create(name='Power Armor')
        cls.category_2 = Category.objects.create(name='Pip-Boy')

        # Setting up sparepart data
        cls.sparepart = Sparepart.objects.create(
                            name='X-01 Power Armor',
                            partnumber='X-01 HFI9-23',
                            quantity=50,
                            motor_type='Enclave',
                            sparepart_type='Protect',
                            price=5400000,
                            workshop_price=5300000,
                            install_price=5500000,
                            brand_id=cls.brand_1,
                            category_id=cls.category_1,
                            storage_code='WD-12'
                        )
        cls.sparepart_2 = Sparepart.objects.create(
                            name='Vault 101 Pip-Boy',
                            partnumber='PB-101-23942',
                            quantity=50,
                            motor_type='Vault Dweller',
                            sparepart_type='Vault-Tech',
                            price=5400000,
                            workshop_price=5300000,
                            install_price=5500000,
                            brand_id=cls.brand_2,
                            category_id=cls.category_2,
                            storage_code='WD-12'
                        )

        # Setting up input data
        cls.data = {
            'sparepart': 'X-01 Power Armor',
            'brand': cls.brand_1,
            'category': cls.category_1,
            'motor_type': 'Enclave',
        }

        return super().setUpTestData()

    def test_successfully_searching_sparepart_with_result(self) -> None:
        """
        Ensure user who searching sparepart with correct keyword get correct result
        """
        response = self.client.get(reverse('search_sparepart') + f'?name={self.data["sparepart"]}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['message'], 'Pencarian sparepart berhasil')
        self.assertEqual(response.data['results'][0]['sparepart_id'], self.sparepart.sparepart_id)
        self.assertEqual(response.data['results'][0]['name'], self.sparepart.name)
        self.assertEqual(response.data['results'][0]['brand'], self.sparepart.brand_id.name)
        self.assertEqual(response.data['results'][0]['category'], self.sparepart.category_id.name)
        self.assertEqual(response.data['results'][0]['motor_type'], self.sparepart.motor_type)
        self.assertEqual(response.data['results'][0]['storage_code'], self.sparepart.storage_code)
        self.assertEqual(response.data['results'][0]['price'], str(self.sparepart.price))
        self.assertEqual(response.data['results'][0]['workshop_price'], str(self.sparepart.workshop_price))
        self.assertEqual(response.data['results'][0]['install_price'], str(self.sparepart.install_price))
        self.assertEqual(response.data['results'][0]['quantity'], self.sparepart.quantity)

    def test_successfully_searching_sparepart_with_result_using_few_keywords(self) -> None:
        """
        Ensure user who searching sparepart with correct few keywords get correct result
        """
        response = self.client.get(
            reverse('search_sparepart') + f'?name={self.data["sparepart"]}&motor_type={self.data["motor_type"]}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['message'], 'Pencarian sparepart berhasil')
        self.assertEqual(response.data['results'][0]['sparepart_id'], self.sparepart.sparepart_id)
        self.assertEqual(response.data['results'][0]['name'], self.sparepart.name)
        self.assertEqual(response.data['results'][0]['brand'], self.sparepart.brand_id.name)
        self.assertEqual(response.data['results'][0]['category'], self.sparepart.category_id.name)
        self.assertEqual(response.data['results'][0]['motor_type'], self.sparepart.motor_type)
        self.assertEqual(response.data['results'][0]['storage_code'], self.sparepart.storage_code)
        self.assertEqual(response.data['results'][0]['price'], str(self.sparepart.price))
        self.assertEqual(response.data['results'][0]['workshop_price'], str(self.sparepart.workshop_price))
        self.assertEqual(response.data['results'][0]['install_price'], str(self.sparepart.install_price))
        self.assertEqual(response.data['results'][0]['quantity'], self.sparepart.quantity)

    def test_failed_to_searching_sparepart_without_result(self) -> None:
        """
        Ensure user cannot searching sparepart that doesn't exist get empty result
        """
        response = self.client.get(reverse('search_sparepart') + '?name=random shit')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['count_item'], 0)
        self.assertEqual(response.data['message'], 'Sparepart yang dicari tidak ditemukan')


class ChangePasswordTestCase(APITestCase):
    change_pass_url = reverse('password_change')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.data = {
            'new_password1': 'XandarGone2',
            'new_password2': 'XandarGone2',
            'old_password': 'NovaPrimeAnnahilations',
        }

        cls.wrong_old_password = {
            'new_password1': 'XandarGone2',
            'new_password2': 'XandarGone2',
            'old_password': 'GreenLanterns',
        }

        cls.weak_password = {
            'new_password1': '123asd',
            'new_password2': '123asd',
            'old_password': 'NovaPrimeAnnahilations',
        }

        return super().setUpTestData()

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='richardrider',
            password='NovaPrimeAnnahilations',
            email='chad.bladess@gmail.com'
        )

        return super().setUp()

    def test_user_successfully_change_password(self) -> None:
        """
        Ensure user can change password successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_pass_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nonlogin_user_failed_to_change_password(self) -> None:
        """
        Ensure non-login user cannot change password
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.change_pass_url, self.data)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_failed_to_change_password_with_wrong_old_password(self) -> None:
        """
        Ensure user cannot change password using wrong old password
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_pass_url, self.wrong_old_password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_failed_to_change_password_with_weak_password(self) -> None:
        """
        Ensure user cannot change password using weak password
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_pass_url, self.weak_password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResetPasswordTestCase(APITestCase):
    reset_password_url = reverse('password_reset')
    reset_password_confirm = reverse('rest_password_reset_confirm')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username='richardrider',
            password='NovaPrimeAnnahilations',
            email='chad.bladess@gmail.com'
        )
        cls.user.is_active = True
        cls.user.save()

        return super().setUpTestData()

    def _generate_uid_and_token(self, user):
        result = {}
        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account.forms import default_token_generator
            from allauth.account.utils import user_pk_to_url_str
            result['uid'] = user_pk_to_url_str(user)
        else:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.encoding import force_bytes
            from django.utils.http import urlsafe_base64_encode
            result['uid'] = urlsafe_base64_encode(force_bytes(user.pk))
        result['token'] = default_token_generator.make_token(user)
        return result

    def test_user_successfully_get_email_in_reset_password(self) -> None:
        """
        Ensure user can get email to reset user's account password successfully
        """
        response = self.client.post(self.reset_password_url, {'email': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_user_failed_to_get_email_with_wrong_email_in_reset_password(self) -> None:
        """
        Ensure user cannot get email to reset account password using wrong email data
        """
        response = self.client.post(self.reset_password_url, {'email': 'wrong@gmail.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

    def test_user_successfully_reset_password_confirm(self) -> None:
        """
        Ensure user can reset user's account password successfully
        """
        self.url_kwargs = self._generate_uid_and_token(self.user)

        # Setting up data input
        self.data = {
            'new_password1': 'NewWarriors31',
            'new_password2': 'NewWarriors31',
            'uid': force_str(self.url_kwargs['uid']),
            'token': self.url_kwargs['token'],
        }

        response = self.client.post(self.reset_password_confirm, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_failed_to_reset_password_confirm_with_wrong_data(self) -> None:
        """
        Ensure user cannot reset user's account password with wrong data
        """
        self.url_kwargs = self._generate_uid_and_token(self.user)

        # Setting up wrong data input
        self.wrong_data = {
            'new_password1': 'NewWarriors31',
            'new_password2': 'NewWarriors31',
            'uid': force_str(self.url_kwargs['uid']),
            'token': 'wrong token',
        }

        response = self.client.post(self.reset_password_confirm, self.wrong_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
