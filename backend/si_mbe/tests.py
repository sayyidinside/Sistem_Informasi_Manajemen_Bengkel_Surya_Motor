from datetime import date, timedelta

from django.utils.encoding import force_str
from django.conf import settings
from django.core import mail
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from si_mbe.models import (Brand, Extend_user, Restock, Restock_detail, Role,
                           Sales, Sales_detail, Sparepart, Supplier)


# Create your tests here.
class SetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and non-admin user
        cls.role = Role.objects.create(name='Admin')
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Extend_user.objects.create(user=cls.user, role_id=cls.role, name='Richard Rider')

        cls.nonadmin_role = Role.objects.create(name='Karyawan')
        cls.nonadmin_user = User.objects.create_user(username='Phalanx', password='TryintoTakeOver')
        Extend_user.objects.create(user=cls.nonadmin_user, role_id=cls.nonadmin_role)

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
        cls.name = 'aki 1000CC'
        cls.partnumber = 'AB17623-ha2092d'

        Sparepart.objects.create(
            name=cls.name,
            partnumber=cls.partnumber,
            quantity=50,
            motor_type='Yamaha Nmax',
            sparepart_type='24Q-22',
            price=5400000,
            grosir_price=5300000,
            brand_id=None
        )

        return super().setUpTestData()

    def test_successfully_searching_sparepart_with_result(self) -> None:
        """
        Ensure user who searching sparepart with correct keyword get correct result
        """
        response = self.client.get(reverse('search_sparepart') + f'?q={self.name}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['results'][0]['partnumber'], self.partnumber)
        self.assertEqual(response.data['message'], 'Pencarian sparepart berhasil')

    def test_successfully_searching_sparepart_without_result(self) -> None:
        """
        Ensure user who searching sparepart that doesn't exist get empty result
        """
        response = self.client.get(reverse('search_sparepart') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 0)
        self.assertEqual(response.data['message'], 'Sparepart yang dicari tidak ditemukan')


class DashboardTestCase(SetTestCase):
    dashboard_url = reverse('dashboard')

    def test_admin_successfully_accessed_admin_dashboard(self) -> None:
        """
        Ensure user can access admin dashboard
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nonlogin_user_failed_to_access_admin_dashboard(self) -> None:
        """
        Ensure non-login user cannot access admin dashboard
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_admin_dashboard(self) -> None:
        """
        Ensure non-admin user cannot access admin dashboard
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class SparepartDataListTestCase(SetTestCase):
    sparepart_data_list_url = reverse('sparepart_data_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up sparepart data
        cls.name = 'Spakbord C70'
        cls.partnumber = 'AB17623-ha2092d'
        for i in range(3):
            Sparepart.objects.create(
                name=f'{cls.name}{i}',
                partnumber=f'{cls.partnumber}{i}',
                quantity=50,
                motor_type='Yamaha Nmax',
                sparepart_type='24Q-22',
                price=5400000,
                grosir_price=5300000,
                brand_id=None
            )

        return super().setUpTestData()

    def test_admin_successfully_access_sparepart_data_list(self) -> None:
        """
        Ensure admin can get sparepart data list successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.sparepart_data_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 3)
        self.assertEqual(response.data['results'][0]['name'], f'{self.name}0')
        self.assertEqual(response.data['results'][0]['partnumber'], f'{self.partnumber}0')

    def test_nonlogin_user_failed_to_access_sparepart_data_list(self) -> None:
        """
        Ensure non-login user cannot access sparepart data list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.sparepart_data_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_sparepart_data_list(self) -> None:
        """
        Ensure non-admin user cannot access sparepart data list
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.get(self.sparepart_data_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class SparepartDataAddTestCase(SetTestCase):
    sparepart_data_add_url = reverse('sparepart_data_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Creating data that gonna be use as input
        cls.data_sparepart = {
            'name': 'Milano Buster T-194',
            'partnumber': '127hash-19as88l0',
            'quantity': 50,
            'motor_type': 'Yamaha Nmax',
            'sparepart_type': '24Q-22',
            'price': 5400000,
            'grosir_price': 5300000,
        }

        return super().setUpTestData()

    def test_admin_successfully_add_new_sparepart_data(self) -> None:
        """
        Ensure admin can add new sparepart data successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.sparepart_data_add_url, self.data_sparepart)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.data_sparepart['name'])
        self.assertEqual(response.data['partnumber'], self.data_sparepart['partnumber'])
        self.assertEqual(int(response.data['price']), self.data_sparepart['price'])
        self.assertEqual(response.data['message'], 'Data sparepart berhasil ditambah')

    def test_nonlogin_user_failed_to_add_new_sparepart_data(self) -> None:
        """
        Ensure non-login user cannot add new sparepart data
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.sparepart_data_add_url, self.data_sparepart)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_add_new_sparepart_data(self) -> None:
        """
        Ensure non-admin user cannot add new sparepart data
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.post(self.sparepart_data_add_url, self.data_sparepart)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_add_sparepart_with_empty_data(self) -> None:
        """
        Ensure admin cannot add data sparepart with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.sparepart_data_add_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data sparepart tidak sesuai / tidak lengkap')

    def test_admin_failed_to_add_sparepart_with_partially_empty_data(self) -> None:
        """
        Ensure admin cannot add data sparepart with partially empty data / input
        """
        self.partial_data = {'name': 'Milano Buster T-194', 'partnumber': '127hash-19as88l0', 'quantity': 50}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.sparepart_data_add_url, self.partial_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data sparepart tidak sesuai / tidak lengkap')


class SparepartDataUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up new data to update sparepart data
        cls.data = {
            'name': 'Razor Crest PF-30',
            'partnumber': '7asAA-9293B',
            'quantity': 20,
            'motor_type': 'Navigations',
            'sparepart_type': '24Q-22',
            'price': 5800000,
            'grosir_price': 5400000,
        }

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up sparepart data
        for i in range(3):
            Sparepart.objects.create(
                name=f'Razor Crest PF-3{i}',
                partnumber=f'7asAA-9293B{i}',
                quantity=23,
                motor_type='Navigations',
                sparepart_type='24Q-22',
                price=5800000,
                grosir_price=5400000,
                brand_id=None
            )

        # Getting newly added sparepart it's sparepart_id then set it to kwargs in reverse url
        self.sparepart_id = Sparepart.objects.get(name='Razor Crest PF-30').sparepart_id
        self.sparepart_data_update_url = reverse('sparepart_data_update', kwargs={'sparepart_id': self.sparepart_id})

        return super().setUp()

    def test_admin_successfully_update_sparepart_data(self) -> None:
        """
        Ensure admin can update sparepart data successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.sparepart_data_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Data sparepart berhasil dirubah')
        self.assertEqual(response.data['name'], self.data['name'])
        self.assertEqual(response.data['partnumber'], self.data['partnumber'])
        self.assertEqual(int(response.data['quantity']), self.data['quantity'])
        self.assertEqual(response.data['motor_type'], self.data['motor_type'])
        self.assertEqual(response.data['sparepart_type'], self.data['sparepart_type'])
        self.assertEqual(int(response.data['price']), self.data['price'])
        self.assertEqual(int(response.data['grosir_price']), self.data['grosir_price'])

    def test_nonlogin_user_failed_to_update_sparepart_data(self) -> None:
        """
        Ensure non-login user cannot update sparepart data
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.sparepart_data_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_update_sparepart_data(self) -> None:
        """
        Ensure non-admin user cannot update sparepart data
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.put(self.sparepart_data_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_update_nonexist_sparepart_data(self) -> None:
        """
        Ensure admin cannot / Failed update non-exist sparepart data
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('sparepart_data_update', kwargs={'sparepart_id': 4563}),
                                   self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data sparepart tidak ditemukan')

    def test_admin_failed_to_update_sparepart_with_empty_data(self) -> None:
        """
        Ensure admin cannot update data sparepart with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.sparepart_data_update_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data sparepart tidak sesuai / tidak lengkap')

    def test_admin_failed_to_update_sparepart_with_partially_empty_data(self) -> None:
        """
        Ensure admin cannot update data sparepart with partially empty data / input
        """
        self.partial_data = {'name': 'Razor Crest PF-0', 'partnumber': '127hash-19as88l0', 'quantity': 10}
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.sparepart_data_update_url, self.partial_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data sparepart tidak sesuai / tidak lengkap')


class SparepartDataDeleteTestCase(SetTestCase):
    def setUp(self) -> None:
        # Setting up sparepart data
        for i in range(3):
            Sparepart.objects.create(
                name=f'Fondor Haulcraft W{i}',
                partnumber=f'8ahb0{i}-D489',
                quantity=5,
                motor_type='Trader Ship',
                sparepart_type='24Q-22',
                price=800000,
                grosir_price=750000,
                brand_id=None
            )

        # Getting newly added sparepart it's sparepart_id then set it to kwargs in reverse url
        self.sparepart_id = Sparepart.objects.get(name='Fondor Haulcraft W1').sparepart_id
        self.sparepart_data_delete_url = reverse('sparepart_data_delete', kwargs={'sparepart_id': self.sparepart_id})

        return super().setUp()

    def test_admin_successfully_delete_sparepart_data(self) -> None:
        """
        Ensure admin can delete sparepart data successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.sparepart_data_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data sparepart berhasil dihapus')
        self.assertEqual(len(Sparepart.objects.all()), 2)

    def test_nonlogin_user_failed_to_delete_sparepart_data(self) -> None:
        """
        Ensure non-login user cannot delete sparepart data
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.sparepart_data_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_delete_sparepart_data(self) -> None:
        """
        Ensure non-admin user cannot delete sparepart data
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.delete(self.sparepart_data_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_delete_nonexist_sparepart_data(self) -> None:
        """
        Ensure admin cannot to delete non-exist sparepart data
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('sparepart_data_delete', kwargs={'sparepart_id': 4563}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data sparepart tidak ditemukan')


class SalesListTestCase(SetTestCase):
    sales_url = reverse('sales_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up sparepart data and getting their id
        for i in range(5):
            Sparepart.objects.create(
                name=f'Gaia Memory D-9-2{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Fuuto Wind',
                sparepart_type='USB',
                price=5400000,
                grosir_price=5300000,
                brand_id=None
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up sales data and getting their id
        for i in range(2):
            Sales.objects.create(
                customer_name='Brandon Sanderson',
                customer_contact='085456105311',
            )

        cls.sales = Sales.objects.all()

        # Setting up sales detail data and getting their id
        cls.sales_details_1 = Sales_detail.objects.create(
            quantity=2,
            is_grosir=False,
            sales_id=cls.sales[0],
            sparepart_id=cls.spareparts[3]
        )
        cls.sales_details_2 = Sales_detail.objects.create(
            quantity=5,
            is_grosir=False,
            sales_id=cls.sales[1],
            sparepart_id=cls.spareparts[0]
        )
        cls.sales_details_3 = Sales_detail.objects.create(
            quantity=3,
            is_grosir=False,
            sales_id=cls.sales[1],
            sparepart_id=cls.spareparts[1]
        )

        return super().setUpTestData()

    def test_admin_successfully_access_sales_list(self) -> None:
        """
        Ensure admin can get sales list
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.sales_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'], [
            {
                'sales_id': self.sales[0].sales_id,
                'customer_name': 'Brandon Sanderson',
                'customer_contact': '085456105311',
                'is_paid_off': False,
                'content': [
                    {
                        'sales_detail_id': self.sales_details_1.sales_detail_id,
                        'sparepart': self.spareparts[3].name,
                        'quantity': 2,
                        'is_grosir': False,
                    }
                ]
            },
            {
                'sales_id': self.sales[1].sales_id,
                'customer_name': 'Brandon Sanderson',
                'customer_contact': '085456105311',
                'is_paid_off': False,
                'content': [
                    {
                        'sales_detail_id': self.sales_details_2.sales_detail_id,
                        'sparepart': self.spareparts[0].name,
                        'quantity': 5,
                        'is_grosir': False,
                    },
                    {
                        'sales_detail_id': self.sales_details_3.sales_detail_id,
                        'sparepart': self.spareparts[1].name,
                        'quantity': 3,
                        'is_grosir': False,
                    }
                ]
            }
        ])

    def test_nonlogin_user_failed_to_access_sales_list(self) -> None:
        """
        Ensure non-login user cannot access sales list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.sales_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_sales_list(self) -> None:
        """
        Ensure non-admin user cannot access sales list
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.get(self.sales_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class SalesAddTestCase(SetTestCase):
    sales_add_url = reverse('sales_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'Core Fluid P-{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Queen Jet',
                sparepart_type='Oil',
                price=5400000,
                grosir_price=5300000,
                brand_id=None
            )

        cls.spareparts = Sparepart.objects.all()

        # Creating data that gonna be use as input
        cls.data = {
            'customer_name': 'Matt Mercer',
            'customer_contact': '085634405602',
            'is_paid_off': False,
            'content': [
                {
                    'sparepart_id': cls.spareparts[1].sparepart_id,
                    'quantity': 1,
                    'is_grosir': False,
                },
                {
                    'sparepart_id': cls.spareparts[0].sparepart_id,
                    'quantity': 30,
                    'is_grosir': True,
                }
            ]
        }

        return super().setUpTestData()

    def test_admin_successfully_add_sales(self) -> None:
        """
        Ensure admin can add new sales data with it's content
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.sales_add_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Data penjualan berhasil ditambah')
        self.assertEqual(response.data['customer_name'], 'Matt Mercer')
        self.assertEqual(len(response.data['content']), 2)
        self.assertEqual(response.data['content'][0]['sparepart_id'], self.spareparts[1].sparepart_id)
        self.assertEqual(response.data['content'][0]['quantity'], 1)
        self.assertEqual(response.data['content'][0]['is_grosir'], False)

    def test_nonlogin_user_failed_to_add_sales(self) -> None:
        """
        Ensure non-login cannot add new sales data with it's content
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.sales_add_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_failed_to_add_sales(self) -> None:
        """
        Ensure non-admin cannot add new sales data with it's content
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.post(self.sales_add_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_add_sales_with_empty_data(self) -> None:
        """
        Ensure admin cannot add sales with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.sales_add_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data penjualan tidak sesuai / tidak lengkap')

    def test_admin_failed_to_add_sales_with_partially_empty_data(self) -> None:
        """
        Ensure admin cannot add data sales with partially empty data / input
        """
        self.partial_data = {'customer_name': 'Matt Mercer', 'customer_contact': '085634405602', 'is_paid_off': False}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.sales_add_url, self.partial_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data penjualan tidak sesuai / tidak lengkap')


class SalesUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'B-F-Gun {i}',
                partnumber=f'JKL03uf-U-{i}',
                quantity=int(f'5{i}'),
                motor_type='Dreadnought',
                sparepart_type='Weapon',
                price=105000,
                grosir_price=100000,
                brand_id=None
            )

        cls.spareparts = Sparepart.objects.all()

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up sales data and getting their id
        self.sales = Sales.objects.create(
            customer_name='Clem Andor',
            customer_contact='085425502660',
        )

        # Getting newly added sales it's sales_id then set it to kwargs in reverse url
        self.sales_update_url = reverse('sales_update', kwargs={'sales_id': self.sales.sales_id})

        # Setting up sales detail data and getting their id
        self.sales_detail_1 = Sales_detail.objects.create(
            quantity=1,
            is_grosir=False,
            sales_id=self.sales,
            sparepart_id=self.spareparts[2]
        )
        self.sales_detail_2 = Sales_detail.objects.create(
            quantity=31,
            is_grosir=True,
            sales_id=self.sales,
            sparepart_id=self.spareparts[0]
        )

        # Creating data that gonna be use as input
        self.data = {
            'customer_name': 'Cassian Andor',
            'customer_contact': '087425502660',
            'is_paid_off': True,
            'content': [
                {
                    'sales_detail_id': self.sales_detail_1.sales_detail_id,
                    'sparepart_id': self.spareparts[2].sparepart_id,
                    'quantity': 2,
                    'is_grosir': False,
                },
                {
                    'sales_detail_id': self.sales_detail_2.sales_detail_id,
                    'sparepart_id': self.spareparts[0].sparepart_id,
                    'quantity': 30,
                    'is_grosir': True,
                }
            ]
        }

        return super().setUp()

    def test_admin_successfuly_update_sales(self) -> None:
        """
        Ensure admin can update sales data successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.sales_update_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Data penjualan berhasil dirubah')
        self.assertEqual(response.data['customer_name'], 'Cassian Andor')
        self.assertEqual(len(response.data['content']), 2)
        self.assertEqual(response.data['content'][0]['sparepart_id'], self.spareparts[2].sparepart_id)
        self.assertEqual(response.data['content'][0]['quantity'], 2)
        self.assertEqual(response.data['content'][0]['is_grosir'], False)
        self.assertEqual(response.data['content'][1]['sparepart_id'], self.spareparts[0].sparepart_id)
        self.assertEqual(response.data['content'][1]['quantity'], 30)
        self.assertEqual(response.data['content'][1]['is_grosir'], True)

    def test_nonlogin_failed_to_update_sales(self) -> None:
        """
        Ensure non-login user cannot update sales
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.sales_update_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_update_sales(self) -> None:
        """
        Ensure non-admin user cannot update sales
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.put(self.sales_update_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_update_nonexist_sales(self) -> None:
        """
        Ensure admin cannot / Failed update non-exist sales
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('sales_update', kwargs={'sales_id': 4152}),
                                   self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data penjualan tidak ditemukan')

    def test_admin_failed_to_update_sales_with_empty_data(self) -> None:
        """
        Ensure admin cannot update sales with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.sales_update_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data penjualan tidak sesuai / tidak lengkap')

    def test_admin_failed_to_update_sales_with_partially_empty_data(self) -> None:
        """
        Ensure admin cannot update sales with partially empty data / input
        """
        self.partail_data = {'customer_name': 'Cassian Andor', 'customer_contact': '087425502660'}
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.sales_update_url, self.partail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data penjualan tidak sesuai / tidak lengkap')


class SalesDeleteTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'spelljammer {i}L-1',
                partnumber=f'J8OI0-h8{i}',
                quantity=int(f'7{i}'),
                motor_type='Space Ship',
                sparepart_type='Core',
                price=105000,
                grosir_price=100000,
                brand_id=None
            )

        cls.spareparts = Sparepart.objects.all()

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up sales data and getting their id
        self.sales = Sales.objects.create(
            customer_name='Zurat Gracdion',
            customer_contact='085425045263',
        )

        # Getting newly added sales it's sales_id then set it to kwargs in reverse url
        self.sales_delete_url = reverse('sales_delete', kwargs={'sales_id': self.sales.sales_id})

        # Setting up sales detail data
        Sales_detail.objects.create(
            quantity=1,
            is_grosir=False,
            sales_id=self.sales,
            sparepart_id=self.spareparts[2]
        )
        Sales_detail.objects.create(
            quantity=51,
            is_grosir=True,
            sales_id=self.sales,
            sparepart_id=self.spareparts[0]
        )

        return super().setUp()

    def test_admin_successfully_delete_sales(self) -> None:
        """
        Ensure admin can delete sales successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.sales_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data penjualan berhasil dihapus')
        self.assertEqual(len(Sales.objects.all()), 0)
        self.assertEqual(len(Sales_detail.objects.all()), 0)

    def test_nonlogin_user_failed_to_delete_sales(self) -> None:
        """
        Ensure non-login user cannot delete sales
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.sales_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_delete_sales(self) -> None:
        """
        Ensure non-admin user cannot delete sales
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.delete(self.sales_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_delete_nonexist_sales(self) -> None:
        """
        Ensure admin cannot / failed to delete non-exist sales
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('sales_delete', kwargs={'sales_id': 5635}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data penjualan tidak ditemukan')


class RestockListTestCase(SetTestCase):
    restock_url = reverse('restock_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up supplier
        cls.supplier = Supplier.objects.create(
            name='Arasaka',
            address='Night City',
            contact_number='084894564563',
            salesman_name='Saburo Arasaka',
            salesman_contact='084523015663'
        )

        # Setting up sparepart data and getting their id
        for i in range(4):
            Sparepart.objects.create(
                name=f'Sandevistan PV-{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Cyberpunk',
                sparepart_type='Cyberware',
                price=4700000,
                grosir_price=4620000,
                brand_id=None
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up restock data and getting their object
        for i in range(2):
            Restock.objects.create(
                no_faktur=f'URH45/28394/2022-N{i}D',
                due_date=date(2023, 4, 13),
                supplier_id=cls.supplier,
                is_paid_off=False
            )

        cls.restocks = Restock.objects.all()

        # Setting up restock detail data and getting their id
        cls.restock_detail_1 = Restock_detail.objects.create(
            quantity=2,
            individual_price=4550000,
            restock_id=cls.restocks[0],
            sparepart_id=cls.spareparts[3]
        )
        cls.restock_detail_2 = Restock_detail.objects.create(
            quantity=5,
            individual_price=4550000,
            restock_id=cls.restocks[1],
            sparepart_id=cls.spareparts[0]
        )
        cls.restock_detail_3 = Restock_detail.objects.create(
            quantity=3,
            individual_price=4550000,
            restock_id=cls.restocks[1],
            sparepart_id=cls.spareparts[1]
        )

        return super().setUpTestData()

    def test_admin_successfully_access_restock_list(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.restock_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'], [
            {
                'restock_id': self.restocks[0].restock_id,
                'no_faktur': 'URH45/28394/2022-N0D',
                'due_date': '13-04-2023',
                'supplier': self.supplier.name,
                'is_paid_off': False,
                'content': [
                    {
                        'restock_detail_id': self.restock_detail_1.restock_detail_id,
                        'sparepart': self.spareparts[3].name,
                        'individual_price':'4550000',
                        'quantity': 2,
                    }
                ]
            },
            {
                'restock_id': self.restocks[1].restock_id,
                'no_faktur': 'URH45/28394/2022-N1D',
                'due_date': '13-04-2023',
                'supplier': self.supplier.name,
                'is_paid_off': False,
                'content': [
                    {
                        'restock_detail_id': self.restock_detail_2.restock_detail_id,
                        'sparepart': self.spareparts[0].name,
                        'individual_price':'4550000',
                        'quantity': 5,
                    },
                    {
                        'restock_detail_id': self.restock_detail_3.restock_detail_id,
                        'sparepart': self.spareparts[1].name,
                        'individual_price':'4550000',
                        'quantity': 3,
                    }
                ]
            }
        ])

    def test_nonlogin_failed_to_access_restock_list(self) -> None:
        """
        Ensure non-login user cannot access restock list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.restock_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_restock_list(self) -> None:
        """
        Ensure non-admin user cannot access restock list
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.get(self.restock_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class RestockAddTestCase(SetTestCase):
    restock_add_url = reverse('restock_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up supplier
        cls.supplier = Supplier.objects.create(
            name='Parker Industries',
            address='New York st.long walk',
            contact_number='084526301053',
            salesman_name='Peter Parker',
            salesman_contact='084105634154'
        )

        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'Webware V.{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Wrist Device',
                sparepart_type='Braclet',
                price=5400000,
                grosir_price=5300000,
                brand_id=None
            )

        cls.spareparts = Sparepart.objects.all()

        # Creating data that gonna be use as input
        cls.data = {
            'no_faktur': 'URH45/28394/2022-N1D',
            'due_date': date(2023, 4, 13),
            'supplier_id': cls.supplier.supplier_id,
            'is_paid_off': False,
            'content': [
                {
                    'sparepart_id': cls.spareparts[0].sparepart_id,
                    'individual_price':4700000,
                    'quantity': 150,
                },
                {
                    'sparepart_id': cls.spareparts[1].sparepart_id,
                    'individual_price':3500000,
                    'quantity': 60,
                }
            ]
        }

        return super().setUpTestData()

    def test_admin_successfully_add_restock(self) -> None:
        """
        Ensure admin can add new restock data with it's content
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.restock_add_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Data pengadaan berhasil ditambah')
        self.assertEqual(response.data['no_faktur'], 'URH45/28394/2022-N1D')
        self.assertEqual(response.data['due_date'], '13-04-2023')
        self.assertEqual(response.data['supplier_id'], self.supplier.supplier_id)
        self.assertEqual(response.data['is_paid_off'], False)
        self.assertEqual(len(response.data['content']), 2)
        self.assertEqual(response.data['content'][0]['sparepart_id'], self.spareparts[0].sparepart_id)
        self.assertEqual(response.data['content'][0]['individual_price'], '4700000')
        self.assertEqual(response.data['content'][0]['quantity'], 150)
        self.assertEqual(response.data['content'][1]['sparepart_id'], self.spareparts[1].sparepart_id)
        self.assertEqual(response.data['content'][1]['individual_price'], '3500000')
        self.assertEqual(response.data['content'][1]['quantity'], 60)

    def test_nonlogin_user_failed_to_add_restock(self) -> None:
        """
        Ensure non-admin cannot add new restock data with it's content
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.restock_add_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_failed_to_add_restock(self) -> None:
        """
        Ensure non-admin cannot add new restock data with it's content
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.post(self.restock_add_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_add_restock_with_empty_data(self) -> None:
        """
        Ensure admin cannot add new restock data with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.restock_add_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data pengadaan tidak sesuai / tidak lengkap')

    def test_admin_failed_to_add_restock_with_partially_empty_data(self) -> None:
        """
        Ensure admin cannot add new restock data with partially empty data / input
        """
        self.partial_data = {'no_faktur': 'URH45/28394/2022-N1D',
                             'due_date': date(2023, 4, 13),
                             'is_paid_off': True}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.restock_add_url, self.partial_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data pengadaan tidak sesuai / tidak lengkap')


class RestockUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up supplier
        cls.supplier = Supplier.objects.create(
            name='Invulnerable Vagrant',
            address='Zadash market disctrict',
            contact_number='084526301053',
            salesman_name='Pumat Sol',
            salesman_contact='084105634154'
        )

        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'Potion of Haste +{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Adventurer',
                sparepart_type='Potion',
                price=5400000,
                grosir_price=5300000,
                brand_id=None
            )

        cls.spareparts = Sparepart.objects.all()

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up restock detail data
        self.restock = Restock.objects.create(
                no_faktur='78SDFBH/2022-YE/FA89',
                due_date=date(2023, 4, 13),
                supplier_id=self.supplier,
                is_paid_off=False
            )

        # Getting newly added restock it's restock_id then set it to kwargs in reverse url
        self.restock_update_url = reverse('restock_update', kwargs={'restock_id': self.restock.restock_id})

        # Setting up restock detail data and getting their id
        self.restock_detail_1 = Restock_detail.objects.create(
            quantity=200,
            individual_price=4550000,
            restock_id=self.restock,
            sparepart_id=self.spareparts[0]
        )
        self.restock_detail_2 = Restock_detail.objects.create(
            quantity=50,
            individual_price=450000,
            restock_id=self.restock,
            sparepart_id=self.spareparts[1]
        )

        # Creating data that gonna be use as input
        self.data = {
            'no_faktur': '78SDFBH/2022-YE/FA89',
            'due_date': date(2023, 4, 13),
            'supplier_id': self.supplier.supplier_id,
            'is_paid_off': True,
            'content': [
                {
                    'restock_detail_id': self.restock_detail_1.restock_detail_id,
                    'sparepart_id': self.spareparts[0].sparepart_id,
                    'individual_price':4550000,
                    'quantity': 200,
                },
                {
                    'restock_detail_id': self.restock_detail_2.restock_detail_id,
                    'sparepart_id': self.spareparts[1].sparepart_id,
                    'individual_price':450000,
                    'quantity': 50,
                }
            ]
        }

        return super().setUp()

    def test_admin_successfully_update_restock(self) -> None:
        """
        Ensure admin can update restock data successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.restock_update_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Data pengadaan berhasil dirubah')
        self.assertEqual(response.data['no_faktur'], '78SDFBH/2022-YE/FA89')
        self.assertEqual(response.data['due_date'], '13-04-2023')
        self.assertEqual(response.data['is_paid_off'], True)
        self.assertEqual(len(response.data['content']), 2)
        self.assertEqual(response.data['content'][0]['restock_detail_id'], self.restock_detail_1.restock_detail_id)
        self.assertEqual(response.data['content'][0]['sparepart_id'], self.spareparts[0].sparepart_id)
        self.assertEqual(response.data['content'][0]['individual_price'], '4550000')
        self.assertEqual(response.data['content'][0]['quantity'], 200)
        self.assertEqual(response.data['content'][1]['restock_detail_id'], self.restock_detail_2.restock_detail_id)
        self.assertEqual(response.data['content'][1]['sparepart_id'], self.spareparts[1].sparepart_id)
        self.assertEqual(response.data['content'][1]['individual_price'], '450000')
        self.assertEqual(response.data['content'][1]['quantity'], 50)

    def test_nonlogin_failed_to_update_restock(self) -> None:
        """
        Ensure non-login user cannot update restock
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.restock_update_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_update_restock(self) -> None:
        """
        Ensure non-admin user cannot update restock
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.put(self.restock_update_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_update_nonexist_restock(self) -> None:
        """
        Ensure admin cannot update non-exist restock
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('restock_update', kwargs={'restock_id': 74189}),
                                   self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data pengadaan tidak ditemukan')

    def test_admin_failed_to_update_restock_with_empty_data(self) -> None:
        """
        Ensure admin cannot update restock with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.restock_update_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data pengadaan tidak sesuai / tidak lengkap')

    def test_admin_failed_to_update_restock_with_partially_empty_data(self) -> None:
        """
        Ensure admin cannot update restock with partially empty data / input
        """
        self.partail_data = {'no_faktur': '78SDFBH/2022-YE/FA89',
                             'due_date': date(2023, 4, 13),
                             'supplier_id': self.supplier.supplier_id}
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.restock_update_url, self.partail_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data pengadaan tidak sesuai / tidak lengkap')


class RestockDeleteTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up supplier
        cls.supplier = Supplier.objects.create(
            name="Future Fondations",
            address='New York Street',
            contact_number='084526301053',
            salesman_name='Reed Richards',
            salesman_contact='084105634154'
        )

        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'Ultimate Nulifier {i}',
                partnumber=f'J8OI0-h8{i}',
                quantity=int(f'7{i}'),
                motor_type='Inventions',
                sparepart_type='Device',
                price=105000,
                grosir_price=100000,
                brand_id=None
            )

        cls.spareparts = Sparepart.objects.all()

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up restock detail data
        self.restock = Restock.objects.create(
                no_faktur='78SDFBH/2022-YE/FA89',
                due_date=date(2023, 4, 13),
                supplier_id=self.supplier,
                is_paid_off=False
            )

        # Getting newly added restock it's restock_id then set it to kwargs in reverse url
        self.restock_delete_url = reverse('restock_delete', kwargs={'restock_id': self.restock.restock_id})

        # Setting up restock detail data
        Restock_detail.objects.create(
            quantity=200,
            individual_price=4550000,
            restock_id=self.restock,
            sparepart_id=self.spareparts[0]
        )
        Restock_detail.objects.create(
            quantity=50,
            individual_price=450000,
            restock_id=self.restock,
            sparepart_id=self.spareparts[1]
        )

        return super().setUp()

    def test_admin_successfully_delete_restock(self) -> None:
        """
        Ensure admin can delete restock successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.restock_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data pengadaan berhasil dihapus')
        self.assertEqual(len(Restock.objects.all()), 0)
        self.assertEqual(len(Restock_detail.objects.all()), 0)

    def test_nonlogin_user_failed_to_delete_restock(self) -> None:
        """
        Ensure non-login user cannot delete restock
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.restock_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_delete_restock(self) -> None:
        """
        Ensure non-admin user cannot delete restock
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.delete(self.restock_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_delete_nonexist_restock(self) -> None:
        """
        Ensure admin cannot delete non-exist restock
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('restock_delete', kwargs={'restock_id': 41852}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data pengadaan tidak ditemukan')


class SupplierListTestCase(SetTestCase):
    supplier_url = reverse('supplier_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up supplier
        cls.supplier_1 = Supplier.objects.create(
            name='Alpha Flight',
            address='Canada',
            contact_number='088464105635',
            salesman_name='Logan',
            salesman_contact='080186153054'
        )
        cls.supplier_2 = Supplier.objects.create(
            name='New Warriors',
            address='America',
            contact_number='084108910563',
            salesman_name='Nova Richard Rider',
            salesman_contact='081526348561'
        )
        cls.supplier_3 = Supplier.objects.create(
            name='Quite Council',
            address='Krakoa',
            contact_number='089661056345',
            salesman_name='Charles Xavier',
            salesman_contact='084856105314'
        )

        return super().setUpTestData()

    def test_admin_successfully_access_supplier_list(self) -> None:
        """
        Ensure admin can get supplier list successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.supplier_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 3)
        self.assertEqual(response.data['results'][1]['name'], 'New Warriors')
        self.assertEqual(response.data['results'][1]['address'], 'America')
        self.assertEqual(response.data['results'][1]['contact_number'], '084108910563')
        self.assertEqual(response.data['results'][1]['salesman_name'], 'Nova Richard Rider')
        self.assertEqual(response.data['results'][1]['salesman_contact'], '081526348561')

    def test_nonlogin_user_failed_to_access_supplier_list(self) -> None:
        """
        Ensure non-login user cannot access supplier list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.supplier_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_supplier_list(self) -> None:
        """
        Ensure non-admin user cannot access supplier list
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.get(self.supplier_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class SupplierAddTestCase(SetTestCase):
    supplier_add_url = reverse('supplier_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Creating data that gonna be use as input
        cls.data = {
            'name': 'Mighty Nein',
            'address': 'Wildemount',
            'contact_number': '084110864563',
            'salesman_name': 'Caleb Widogast',
            'salesman_contact': '089854024860'
        }

        return super().setUpTestData()

    def test_admin_successfully_add_supplier(self) -> None:
        """
        Ensure admin can add new supplier successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.supplier_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Data supplier berhasil ditambah')
        self.assertEqual(response.data['name'], self.data['name'])
        self.assertEqual(response.data['address'], self.data['address'])
        self.assertEqual(response.data['contact_number'], self.data['contact_number'])
        self.assertEqual(response.data['salesman_name'], self.data['salesman_name'])
        self.assertEqual(response.data['salesman_contact'], self.data['salesman_contact'])

    def test_nonlogin_user_failed_to_add_new_supplier(self) -> None:
        """
        Ensure non-login user cannot add new supplier
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.supplier_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_add_new_supplier(self) -> None:
        """
        Ensure non-admin user cannot add new supplier
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.post(self.supplier_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_add_supplier_with_empty_data(self) -> None:
        """
        Ensure admin cannot add supplier with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.supplier_add_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data supplier tidak sesuai / tidak lengkap')

    def test_admin_failed_to_add_supplier_with_partially_empty_data(self) -> None:
        """
        Ensure admin cannot add supplier with partially empty data / input
        """
        self.partial_data = {'name': 'Chroma Conclave', 'address': 'Exandria'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.supplier_add_url, self.partial_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data supplier tidak sesuai / tidak lengkap')


class SupplierUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Creating data that gonna be use as input
        cls.data = {
            'name': 'Yukumo Village',
            'address': 'Misty Peaks',
            'contact_number': '081526210523',
            'salesman_name': 'Yukumo Village Chief',
            'salesman_contact': '082418596323'
        }

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up supplier
        self.supplier_1 = Supplier.objects.create(
            name='Pokke Village',
            address='Furahiya Mountains',
            contact_number='089661056345',
            salesman_name='Pokke Village Chief',
            salesman_contact='084856105314'
        )
        self.supplier_2 = Supplier.objects.create(
            name='Yukumo',
            address='Misty Peaks',
            contact_number='084108910563',
            salesman_name='Chief',
            salesman_contact='081526348561'
        )

        self.supplier_update_url = reverse('supplier_update', kwargs={'supplier_id': self.supplier_2.supplier_id})

        return super().setUp()

    def test_admin_successfully_update_supplier(self) -> None:
        """
        Ensure admin can update supplier successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.supplier_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Data supplier berhasil dirubah')
        self.assertEqual(response.data['name'], self.data['name'])
        self.assertEqual(response.data['address'], self.data['address'])
        self.assertEqual(response.data['contact_number'], self.data['contact_number'])
        self.assertEqual(response.data['salesman_name'], self.data['salesman_name'])
        self.assertEqual(response.data['salesman_contact'], self.data['salesman_contact'])

    def test_nonlogin_user_failed_to_update_supplier(self) -> None:
        """
        Ensure non-login user cannot update supplier
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.supplier_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_update_supplier(self) -> None:
        """
        Ensure non-admin user cannot update supplier
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.put(self.supplier_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_update_nonexist_supplier(self) -> None:
        """
        Ensure admin cannot update non-exist supplier
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('supplier_update', kwargs={'supplier_id': 52653}),
                                   self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data supplier tidak ditemukan')

    def test_admin_failed_to_update_supplier_with_empty_data(self) -> None:
        """
        Ensure admin cannot update data supplier with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.supplier_update_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data supplier tidak sesuai / tidak lengkap')

    def test_admin_failed_to_update_supplier_with_partially_empty_data(self) -> None:
        """
        Ensure admin cannot update data supplier with partially empty data / input
        """
        self.partial_data = {'name': 'Yukumo Village', 'address': 'Misty Peaks'}
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.supplier_update_url, self.partial_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data supplier tidak sesuai / tidak lengkap')


class SupplierDeleteTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up supplier
        cls.supplier_1 = Supplier.objects.create(
            name='Overwatch',
            address='Brooklyn',
            contact_number='088464105635',
            salesman_name='Winston',
            salesman_contact='080186153054'
        )
        cls.supplier_2 = Supplier.objects.create(
            name='Null Sector',
            address='London',
            contact_number='084108910563',
            salesman_name='Ramattra',
            salesman_contact='081526348561'
        )

        # Getting newly added supplier it's supplier_id then set it to kwargs in reverse url
        cls.supplier_delete_url = reverse('supplier_delete', kwargs={'supplier_id': cls.supplier_1.supplier_id})

        return super().setUpTestData()

    def test_admin_successfully_delete_supplier(self) -> None:
        """
        Ensure admin can delete supplier successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.supplier_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data supplier berhasil dihapus')
        self.assertEqual(len(Supplier.objects.all()), 1)

    def test_nonlogin_user_failed_to_delete_supplier(self) -> None:
        """
        Ensure non-login user cannot delete supplier
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.supplier_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_delete_supplier(self) -> None:
        """
        Ensure non-admin user cannot delete supplier
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.delete(self.supplier_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_delete_nonexist_supplier(self) -> None:
        """
        Ensure admin cannot to delete non-exist supplier
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('supplier_delete', kwargs={'supplier_id': 8591}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data supplier tidak ditemukan')


class SalesReportListTestCase(APITestCase):
    sales_report_url = reverse('sales_report_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and owner user
        cls.role = Role.objects.create(name='Admin')
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Extend_user.objects.create(user=cls.user, role_id=cls.role, name='Richard Rider')

        cls.owner_role = Role.objects.create(name='Pemilik')
        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Extend_user.objects.create(user=cls.owner, role_id=cls.owner_role)

        cls.brand = Brand.objects.create(name='Dragon Steel')

        # Setting up sparepart data and getting their object
        for i in range(3):
            Sparepart.objects.create(
                name=f'Cosmere B-{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Fantasy',
                sparepart_type='Book',
                price=5400000,
                grosir_price=5300000,
                brand_id=cls.brand
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up sales data and getting their object
        cls.sales_1 = Sales.objects.create(
                customer_name='Hoid',
                customer_contact='085456105311',
                user_id=cls.user,
            )
        cls.sales_2 = Sales.objects.create(
                customer_name='Vasheer',
                customer_contact='085456105311',
                is_paid_off=True,
                user_id=cls.user,
            )

        # Setting up time data for test comparison
        cls.created_at_1 = cls.sales_1.created_at + timedelta(hours=7)
        cls.updated_at_1 = cls.sales_1.updated_at + timedelta(hours=7)
        cls.created_at_2 = cls.sales_2.created_at + timedelta(hours=7)
        cls.updated_at_2 = cls.sales_2.updated_at + timedelta(hours=7)

        return super().setUpTestData()

    def test_owner_successfully_access_sales_report_list(self) -> None:
        """
        Ensure owner can get sales report list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.sales_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'], [
            {
                'sales_id': self.sales_1.sales_id,
                'admin': 'Richard Rider',
                'created_at': self.created_at_1.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': self.updated_at_1.strftime('%d-%m-%Y %H:%M:%S'),
                'customer_name': self.sales_1.customer_name,
                'customer_contact': self.sales_1.customer_contact,
                'is_paid_off': False
            },
            {
                'sales_id': self.sales_2.sales_id,
                'admin': 'Richard Rider',
                'created_at': self.created_at_2.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': self.updated_at_2.strftime('%d-%m-%Y %H:%M:%S'),
                'customer_name': self.sales_2.customer_name,
                'customer_contact': self.sales_2.customer_contact,
                'is_paid_off': True
            }
        ])

    def test_nonlogin_user_failed_to_access_sales_report_list(self) -> None:
        """
        Ensure non-login user cannot access sales report list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.sales_report_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_access_sales_report_list(self) -> None:
        """
        Ensure non-owner user cannot access sales report list
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.sales_report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class SalesReportDetail(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and owner user
        cls.role = Role.objects.create(name='Admin')
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Extend_user.objects.create(user=cls.user, role_id=cls.role, name='Richard Rider')

        cls.owner_role = Role.objects.create(name='Pemilik')
        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Extend_user.objects.create(user=cls.owner, role_id=cls.owner_role)

        cls.brand = Brand.objects.create(name='Steins Gate')

        # Setting up sparepart data and getting their object
        for i in range(3):
            Sparepart.objects.create(
                name=f'el psy congroo S-{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Time Machine',
                sparepart_type='Phrase',
                price=5400000,
                grosir_price=5300000,
                brand_id=cls.brand
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up sales data and getting their object
        cls.sales = Sales.objects.create(
                customer_name='Rintaro Okabe',
                customer_contact='084468104651',
                user_id=cls.user,
            )

        # Getting newly added sales it's sales_id then set it to kwargs in reverse url
        cls.sales_report_detail_url = reverse('sales_report_detail', kwargs={'sales_id': cls.sales.sales_id})

        # Setting up sales detail data and getting their object
        cls.sales_details_1 = Sales_detail.objects.create(
            quantity=15,
            is_grosir=False,
            sales_id=cls.sales,
            sparepart_id=cls.spareparts[2]
        )
        cls.sales_details_2 = Sales_detail.objects.create(
            quantity=10,
            is_grosir=False,
            sales_id=cls.sales,
            sparepart_id=cls.spareparts[0]
        )
        cls.sales_details_3 = Sales_detail.objects.create(
            quantity=20,
            is_grosir=True,
            sales_id=cls.sales,
            sparepart_id=cls.spareparts[1]
        )

        # Setting up time data for test comparison
        cls.created_at_1 = cls.sales.created_at + timedelta(hours=7)
        cls.updated_at_1 = cls.sales.updated_at + timedelta(hours=7)

        return super().setUpTestData()

    def test_owner_successfully_access_sales_report_detail(self) -> None:
        """
        Ensure owner can get sales report detail
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.sales_report_detail_url)
        self.assertEqual(response.data, {
                'sales_id': self.sales.sales_id,
                'admin': 'Richard Rider',
                'created_at': self.created_at_1.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': self.updated_at_1.strftime('%d-%m-%Y %H:%M:%S'),
                'customer_name': self.sales.customer_name,
                'customer_contact': self.sales.customer_contact,
                'is_paid_off': False,
                'content': [
                    {
                        'sales_detail_id': self.sales_details_1.sales_detail_id,
                        'sparepart': self.spareparts[2].name,
                        'quantity': 15,
                        'is_grosir': False
                    },
                    {
                        'sales_detail_id': self.sales_details_2.sales_detail_id,
                        'sparepart': self.spareparts[0].name,
                        'quantity': 10,
                        'is_grosir': False
                    },
                    {
                        'sales_detail_id': self.sales_details_3.sales_detail_id,
                        'sparepart': self.spareparts[1].name,
                        'quantity': 20,
                        'is_grosir': True
                    }
                ]
            }
        )

    def test_nonlogin_user_failed_to_access_sales_report_detail(self) -> None:
        """
        Ensure non-login user cannot access sales report detail
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.sales_report_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_access_sales_report_detail(self) -> None:
        """
        Ensure non-owner user cannot access sales report detail
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.sales_report_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class RestockReportTestCase(APITestCase):
    restock_report_url = reverse('restock_report_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and owner user
        cls.role = Role.objects.create(name='Admin')
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Extend_user.objects.create(user=cls.user, role_id=cls.role, name='Richard Rider')

        cls.owner_role = Role.objects.create(name='Pemilik')
        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Extend_user.objects.create(user=cls.owner, role_id=cls.owner_role)

        # Setting up brand
        cls.brand = Brand.objects.create(name='Cosmic Being')

        # Setting up supplier
        cls.supplier = Supplier.objects.create(
            name='Galactus',
            address='Planet Taa',
            contact_number='084894564563',
            salesman_name='Galan',
            salesman_contact='084523015663'
        )

        # Setting up sparepart data and getting their object
        for i in range(3):
            Sparepart.objects.create(
                name=f'Herald {i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Cosmic Energy',
                sparepart_type='Creature',
                price=4700000,
                grosir_price=4620000,
                brand_id=cls.brand
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up restock data and getting their object
        for i in range(2):
            Restock.objects.create(
                no_faktur=f'URH45/28394/2022-N{i}D',
                due_date=date(2023, 4, 13),
                supplier_id=cls.supplier,
                is_paid_off=False,
                user_id=cls.user
            )

        cls.restocks = Restock.objects.all()

        # Setting up time data for test comparison
        cls.created_at_1 = cls.restocks[0].created_at + timedelta(hours=7)
        cls.updated_at_1 = cls.restocks[0].updated_at + timedelta(hours=7)
        cls.created_at_2 = cls.restocks[1].created_at + timedelta(hours=7)
        cls.updated_at_2 = cls.restocks[1].updated_at + timedelta(hours=7)

        return super().setUpTestData()

    def test_owner_successfully_access_restock_report_list(self):
        """
        Ensure owner can get restock report list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.restock_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'], [
            {
                'restock_id': self.restocks[0].restock_id,
                'admin': 'Richard Rider',
                'created_at': self.created_at_1.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': self.updated_at_1.strftime('%d-%m-%Y %H:%M:%S'),
                'no_faktur': self.restocks[0].no_faktur,
                'is_paid_off': False,
                'due_date': self.restocks[0].due_date.strftime('%d-%m-%Y'),
                'supplier': self.supplier.name,
                'supplier_contact': self.supplier.contact_number,
                'salesman': self.supplier.salesman_name,
                'salesman_contact': self.supplier.salesman_contact
            },
            {
                'restock_id': self.restocks[1].restock_id,
                'admin': 'Richard Rider',
                'created_at': self.created_at_2.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': self.updated_at_2.strftime('%d-%m-%Y %H:%M:%S'),
                'no_faktur': self.restocks[1].no_faktur,
                'is_paid_off': False,
                'due_date': self.restocks[1].due_date.strftime('%d-%m-%Y'),
                'supplier': self.supplier.name,
                'supplier_contact': self.supplier.contact_number,
                'salesman': self.supplier.salesman_name,
                'salesman_contact': self.supplier.salesman_contact
            }
        ])

    def test_nonlogin_user_failed_to_access_restock_report_list(self) -> None:
        """
        Ensure non-login user cannot access restock report list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.restock_report_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_access_restock_report_list(self) -> None:
        """
        Ensure non-owner user cannot access restock report list
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.restock_report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class RestockReportDetailTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and owner user
        cls.role = Role.objects.create(name='Admin')
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Extend_user.objects.create(user=cls.user, role_id=cls.role, name='Richard Rider')

        cls.owner_role = Role.objects.create(name='Pemilik')
        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Extend_user.objects.create(user=cls.owner, role_id=cls.owner_role)

        # Setting up brand
        cls.brand = Brand.objects.create(name='Galactic Empire')

        # Setting up supplier
        cls.supplier = Supplier.objects.create(
            name='narkina 5',
            address='Planet Narkina, Outer Rim',
            contact_number='084894564563',
            salesman_name='Kino Loy',
            salesman_contact='084523015663'
        )

        # Setting up sparepart data and getting their object
        for i in range(3):
            Sparepart.objects.create(
                name=f'Lens Spine D-{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Deathstar',
                sparepart_type='Connector',
                price=4700000,
                grosir_price=4620000,
                brand_id=cls.brand
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up restock data and getting their object
        cls.restock = Restock.objects.create(
                no_faktur=f'URH45/28394/2022-N{i}D',
                due_date=date(2023, 4, 13),
                supplier_id=cls.supplier,
                is_paid_off=False,
                user_id=cls.user
            )

        # Getting newly added sales it's sales_id then set it to kwargs in reverse url
        cls.restock_report_detail_url = reverse('restock_report_detail', kwargs={'restock_id': cls.restock.restock_id})

        # Setting up time data for test comparison
        cls.created_at = cls.restock.created_at + timedelta(hours=7)
        cls.updated_at = cls.restock.updated_at + timedelta(hours=7)

        # Setting up restock detail data and getting their id
        cls.restock_detail_1 = Restock_detail.objects.create(
            quantity=200,
            individual_price=5000000,
            restock_id=cls.restock,
            sparepart_id=cls.spareparts[2]
        )
        cls.restock_detail_2 = Restock_detail.objects.create(
            quantity=500,
            individual_price=400000,
            restock_id=cls.restock,
            sparepart_id=cls.spareparts[0]
        )
        cls.restock_detail_3 = Restock_detail.objects.create(
            quantity=300,
            individual_price=650000,
            restock_id=cls.restock,
            sparepart_id=cls.spareparts[1]
        )

        return super().setUpTestData()

    def test_owner_successfully_access_restock_report_detail(self):
        """
        Ensure owner can get restock report list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.restock_report_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
                'restock_id': self.restock.restock_id,
                'admin': 'Richard Rider',
                'created_at': self.created_at.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': self.updated_at.strftime('%d-%m-%Y %H:%M:%S'),
                'no_faktur': self.restock.no_faktur,
                'is_paid_off': False,
                'due_date': self.restock.due_date.strftime('%d-%m-%Y'),
                'supplier': self.supplier.name,
                'supplier_contact': self.supplier.contact_number,
                'salesman': self.supplier.salesman_name,
                'salesman_contact': self.supplier.salesman_contact,
                'content': [
                    {
                        'restock_detail_id': self.restock_detail_1.restock_detail_id,
                        'sparepart': self.spareparts[2].name,
                        'individual_price':'5000000',
                        'quantity': 200,
                    },
                    {
                        'restock_detail_id': self.restock_detail_2.restock_detail_id,
                        'sparepart': self.spareparts[0].name,
                        'individual_price':'400000',
                        'quantity': 500,
                    },
                    {
                        'restock_detail_id': self.restock_detail_3.restock_detail_id,
                        'sparepart': self.spareparts[1].name,
                        'individual_price':'650000',
                        'quantity': 300,
                    }
                ]
            }
        )

    def test_nonlogin_user_failed_to_access_restock_report_detail(self) -> None:
        """
        Ensure non-login user cannot access restock report detail
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.restock_report_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_access_restock_report_detail(self) -> None:
        """
        Ensure non-owner user cannot access restock report detail
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.restock_report_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class ChangePasswordTestCase(APITestCase):
    change_pass_url = reverse('password_change')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.data = {
            'new_password1': 'XandarGone2',
            'new_password2': 'XandarGone2',
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
        self.old_password = {
            'new_password1': 'XandarGone2',
            'new_password2': 'XandarGone2',
            'old_password': 'GreenLanterns',
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_pass_url, self.old_password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_failed_to_change_password_with_weak_password(self) -> None:
        """
        Ensure user cannot change password using weak password
        """
        self.weak_password = {
            'new_password1': '123asd',
            'new_password2': '123asd',
            'old_password': 'NovaPrimeAnnahilations',
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.change_pass_url, self.weak_password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResetPasswordTestCase(APITestCase):
    reset_password_url = reverse('password_reset')
    reset_password_confirm = reverse('rest_password_reset_confirm')

    @classmethod
    def setUpTestData(cls) -> None:
        return super().setUpTestData()

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='richardrider',
            password='NovaPrimeAnnahilations',
            email='chad.bladess@gmail.com'
        )
        self.user.is_active = True
        self.user.save()

        return super().setUp()

    def _generate_uid_and_token(self, user):
        result = {}
        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account.forms import default_token_generator
            from allauth.account.utils import user_pk_to_url_str
            result['uid'] = user_pk_to_url_str(user)
        else:
            from django.utils.encoding import force_bytes
            from django.contrib.auth.tokens import default_token_generator
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
