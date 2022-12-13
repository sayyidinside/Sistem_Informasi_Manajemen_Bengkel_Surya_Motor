from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from si_mbe.models import Extend_user, Role, Sales, Sales_detail, Sparepart


# Create your tests here.
class SetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and non-admin user
        cls.role = Role.objects.create(name='Admin')
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        cls.extend_user = Extend_user.objects.create(user=cls.user, role_id=cls.role)

        cls.nonadmin_role = Role.objects.create(name='Karyawan')
        cls.nonadmin_user = User.objects.create_user(username='Phalanx', password='TryintoTakeOver')
        cls.extend_user = Extend_user.objects.create(user=cls.nonadmin_user, role_id=cls.nonadmin_role)

        return super().setUpTestData()


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
        self.empty_data = {}
        response = self.client.post(self.login_url, self.empty_data)
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

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='ultraman', password='ultrabrothers')
        self.client.force_authenticate(user=self.user)

    def test_login_user_successfully_logout(self) -> None:
        """
        Ensure user who already login can logout successfully
        """
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

        # Setting up new data to update sparepart data
        self.data = {
            'name': 'Razor Crest PF-30',
            'partnumber': '7asAA-9293B',
            'quantity': 20,
            'motor_type': 'Navigations',
            'sparepart_type': '24Q-22',
            'price': 5800000,
            'grosir_price': 5400000,
        }

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
        data = {'name': 'Razor Crest PF-0', 'partnumber': '127hash-19as88l0', 'quantity': 10}
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.sparepart_data_update_url, data)
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
        Ensure admin cannot / failed to delete non-exist sparepart data
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
        Sales_detail.objects.create(
            quantity=2,
            is_grosir=False,
            sales_id=cls.sales[0],
            sparepart_id=cls.spareparts[3]
        )
        Sales_detail.objects.create(
            quantity=5,
            is_grosir=False,
            sales_id=cls.sales[1],
            sparepart_id=cls.spareparts[0]
        )
        Sales_detail.objects.create(
            quantity=3,
            is_grosir=False,
            sales_id=cls.sales[1],
            sparepart_id=cls.spareparts[1]
        )

        cls.sales_details_id = [
            Sales_detail.objects.get(sparepart_id=cls.spareparts[3].sparepart_id).sales_detail_id,
            Sales_detail.objects.get(sparepart_id=cls.spareparts[0].sparepart_id).sales_detail_id,
            Sales_detail.objects.get(sparepart_id=cls.spareparts[1].sparepart_id).sales_detail_id,
        ]

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
                        'sales_detail_id': self.sales_details_id[0],
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
                        'sales_detail_id': self.sales_details_id[1],
                        'sparepart': self.spareparts[0].name,
                        'quantity': 5,
                        'is_grosir': False,
                    },
                    {
                        'sales_detail_id': self.sales_details_id[2],
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
        data = {'customer_name': 'Matt Mercer', 'customer_contact': '085634405602', 'is_paid_off': False}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.sales_add_url, data)
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
