from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.test import APITestCase
from si_mbe.models import Brand, Profile, Role, Sparepart, Storage


class SetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and non-admin user
        cls.role = Role.objects.create(name='Admin')
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Profile.objects.create(user_id=cls.user, role_id=cls.role, name='Richard Rider')

        cls.owner_role = Role.objects.create(name='Pemilik')
        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Profile.objects.create(user_id=cls.owner, role_id=cls.owner_role)

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
        cls.brand = Brand.objects.create(name='Kymco')

        # Setting up storage data
        cls.storage = Storage.objects.create(
            code='6ABC',
            location='Rak Biru B6'
        )

        # Setting up sparepart data
        cls.sparepart = Sparepart.objects.create(
                            name='aki 1000CC',
                            partnumber='AB17623-ha2092d',
                            quantity=50,
                            motor_type='Yamaha Nmax',
                            sparepart_type='24Q-22',
                            price=5400000,
                            grosir_price=5300000,
                            brand_id=cls.brand,
                            storage_id=cls.storage
                        )

        return super().setUpTestData()

    def test_successfully_searching_sparepart_with_result(self) -> None:
        """
        Ensure user who searching sparepart with correct keyword get correct result
        """
        response = self.client.get(reverse('search_sparepart') + f'?q={self.sparepart.name}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['message'], 'Pencarian sparepart berhasil')
        self.assertEqual(response.data['results'], [
            {
                'sparepart_id': self.sparepart.sparepart_id,
                'name': self.sparepart.name,
                'partnumber': self.sparepart.partnumber,
                'quantity': self.sparepart.quantity,
                'motor_type': self.sparepart.motor_type,
                'sparepart_type': self.sparepart.sparepart_type,
                'brand': self.sparepart.brand_id.name,
                'price': str(self.sparepart.price),
                'grosir_price': str(self.sparepart.grosir_price),
                'location': self.storage.location
            }
        ])

    def test_successfully_searching_sparepart_without_result(self) -> None:
        """
        Ensure user who searching sparepart that doesn't exist get empty result
        """
        response = self.client.get(reverse('search_sparepart') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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


class ProfileDetailTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and non-admin user
        cls.role = Role.objects.create(name='Admin')
        cls.user = User.objects.create_user(
            username='richardrider',
            password='NovaPrimeAnnahilations',
            email='chad.bladess@gmail.com'
        )
        Profile.objects.create(
            user_id=cls.user,
            role_id=cls.role,
            name='Richard Rider',
            contact_number='081256456948'
        )

        cls.nonadmin_role = Role.objects.create(name='Karyawan')
        cls.nonadmin_user = User.objects.create_user(
            username='Phalanx',
            password='TryintoTakeOver',
            email='spacevirusalien@gmail.com'
        )
        Profile.objects.create(
            user_id=cls.nonadmin_user,
            role_id=cls.nonadmin_role,
            name='Ultron',
            contact_number='011011000111'
        )

        return super().setUpTestData()

    def test_user_successfully_access_their_own_profile_detail(self) -> None:
        """
        Ensure user can access their own profile detail successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('profile_detail', kwargs={'user_id': self.user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.profile.name,
            'email': self.user.email,
            'contact_number': self.user.profile.contact_number,
            'role': self.user.profile.role_id.name
        })

    def test_nonlogin_user_failed_to_access_profile_detail(self) -> None:
        """
        Ensure non-login user cannot access profile detail
        """
        response = self.client.get(reverse('profile_detail', kwargs={'user_id': self.user.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_user_failed_to_access_another_user_profile_detail(self) -> None:
        """
        Ensure user cannot access another user / people profile detail
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.get(reverse('profile_detail', kwargs={'user_id': self.user.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_successfully_access_another_user_profile_detail(self) -> None:
        """
        Ensure admin can access another user / people profile detail successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('profile_detail', kwargs={'user_id': self.nonadmin_user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.nonadmin_user.profile.name,
            'email': self.nonadmin_user.email,
            'contact_number': self.nonadmin_user.profile.contact_number,
            'role': self.nonadmin_user.profile.role_id.name
        })


class ProfileUpdateTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and non-admin user
        cls.role = Role.objects.create(name='Admin')
        cls.nonadmin_role = Role.objects.create(name='Karyawan')

        # Setting up admin user and non-admin user details
        cls.user = User.objects.create_user(
            username='richardrider',
            password='NovaPrimeAnnahilations',
            email='chad.bladess@gmail.com'
        )

        cls.nonadmin_user = User.objects.create_user(
            username='Phalanx',
            password='TryintoTakeOver',
            email='spacevirusalien@gmail.com'
        )

        # Setting up admin and non-admin user profile
        Profile.objects.create(
            user_id=cls.user,
            role_id=cls.role,
            name='Richard Rider',
            contact_number='081256456948'
        )

        Profile.objects.create(
            user_id=cls.nonadmin_user,
            role_id=cls.nonadmin_role,
            name='Ultron',
            contact_number='011011000111'
        )

        # Setting up input data
        cls.data = {
            'name': 'Sam Alexander',
            'email': 'kidnova@gmail.com',
            'contact_number': '085263486045',
        }

        return super().setUpTestData()

    def test_user_successfully_update_their_own_profile(self) -> None:
        """
        Ensure user can update their own profile successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            reverse('profile_update', kwargs={'user_id': self.user.pk}),
            self.data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Profile berhasil dirubah')
        self.assertEqual(response.data, {
            'name': self.data['name'],
            'email': self.data['email'],
            'contact_number': self.data['contact_number'],
            'message': 'Profile berhasil dirubah'
        })

    def test_nonlogin_user_failed_to_update_profile(self) -> None:
        """
        Ensure non-login user cannot update profile
        """
        response = self.client.put(
            reverse('profile_update', kwargs={'user_id': self.user.pk}),
            self.data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_user_failed_to_update_another_user_profile(self) -> None:
        """
        Ensure user cannot update another user / people profile
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.put(
            reverse('profile_update', kwargs={'user_id': self.user.pk}),
            self.data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_user_failed_to_update_profile_with_empty_data(self) -> None:
        """
        Ensure user cannot update profile with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            reverse('profile_update', kwargs={'user_id': self.user.pk}),
            {},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data profile tidak sesuai / tidak lengkap')

    def test_user_failed_to_update_profile_with_partial_data(self) -> None:
        """
        Ensure user cannot update profile with partial data / input
        """
        self.partial_data = {'name': 'Self Warlock'}
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            reverse('profile_update', kwargs={'user_id': self.user.pk}),
            self.partial_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data profile tidak sesuai / tidak lengkap')

    def test_admin_successfully_update_other_user_profile(self) -> None:
        """
        Ensure admin can update other user profile successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            reverse('profile_update', kwargs={'user_id': self.nonadmin_user.pk}),
            self.data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Profile berhasil dirubah')
        self.assertEqual(response.data, {
            'name': self.data['name'],
            'email': self.data['email'],
            'contact_number': self.data['contact_number'],
            'message': 'Profile berhasil dirubah'
        })
