from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from si_mbe.models import Extend_user, Role, Sales, Sales_detail, Sparepart


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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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
        Ensure non-login user cannot access admin dashboard
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_user_without_admin_role_cannot_access_admin_dashboard(self) -> None:
        """
        Ensure non-admin user cannot access admin dashboard
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class SparepartDataListTestCase(APITestCase):
    sparepart_data_list_url = reverse('sparepart_data_list')

    def setUp(self) -> None:

        # Setting up sparepart data
        self.name = 'Spakbord C70'
        self.partnumber = 'AB17623-ha2092d'
        for i in range(3):
            Sparepart.objects.create(
                name=f'{self.name}{i}',
                partnumber=f'{self.partnumber}{i}',
                quantity=50,
                motor_type='Yamaha Nmax',
                sparepart_type='24Q-22',
                price=5400000,
                grosir_price=5300000,
                brand_id=None
            )

        # Setting up admin user and non-admin user
        self.role = Role.objects.create(name='Admin')
        self.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        self.extend_user = Extend_user.objects.create(user=self.user, role_id=self.role)
        self.client.force_authenticate(user=self.user)

        self.nonadmin_role = Role.objects.create(name='Karyawan')
        self.nonadmin_user = User.objects.create_user(username='Phalanx', password='TryintoTakeOver')
        self.extend_user = Extend_user.objects.create(user=self.nonadmin_user, role_id=self.nonadmin_role)

    def test_admin_access_sparepart_data_list_successfully(self) -> None:
        """
        Ensure admin can get sparepart data list successfully
        """
        response = self.client.get(self.sparepart_data_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 3)
        self.assertEqual(response.data['results'][0]['name'], f'{self.name}0')
        self.assertEqual(response.data['results'][0]['partnumber'], f'{self.partnumber}0')

    def test_nonlogin_user_cannot_access_sparepart_data_list(self) -> None:
        """
        Ensure non-login user cannot access sparepart data list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.sparepart_data_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_cannot_access_sparepart_data_list(self) -> None:
        """
        Ensure non-admin user cannot access sparepart data list
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.get(self.sparepart_data_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class SparepartDataAddTestCase(APITestCase):
    sparepart_data_add_url = reverse('sparepart_data_add')

    def setUp(self) -> None:
        self.data_sparepart = {
            'name': 'Milano Buster T-194',
            'partnumber': '127hash-19as88l0',
            'quantity': 50,
            'motor_type': 'Yamaha Nmax',
            'sparepart_type': '24Q-22',
            'price': 5400000,
            'grosir_price': 5300000,
        }
        # Setting up admin user and non-admin user
        self.role = Role.objects.create(name='Admin')
        self.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        self.extend_user = Extend_user.objects.create(user=self.user, role_id=self.role)
        self.client.force_authenticate(user=self.user)

        self.nonadmin_role = Role.objects.create(name='Karyawan')
        self.nonadmin_user = User.objects.create_user(username='Phalanx', password='TryintoTakeOver')
        self.extend_user = Extend_user.objects.create(user=self.nonadmin_user, role_id=self.nonadmin_role)

    def test_admin_add_new_sparepart_data_successfully(self) -> None:
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

    def test_nonlogin_user_cannot_add_new_sparepart_data(self) -> None:
        """
        Ensure non-login user cannot add new sparepart data
        """
        # response = self.client.post(reverse('rest_logout'))
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.sparepart_data_add_url, self.data_sparepart)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_cannot_add_new_sparepart_data(self) -> None:
        """
        Ensure non-admin user cannot add new sparepart data
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.post(self.sparepart_data_add_url, self.data_sparepart)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_cannot_add_sparepart_with_empty_data(self) -> None:
        """
        Ensure admin cannot add data sparepart with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.sparepart_data_add_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data sparepart tidak sesuai / tidak lengkap')

    def test_admin_cannot_add_sparepart_with_partially_empty_data(self) -> None:
        """
        Ensure admin cannot add data sparepart with partially empty data / input
        """
        data = {'name': 'Milano Buster T-194', 'partnumber': '127hash-19as88l0', 'quantity': 50}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.sparepart_data_add_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data sparepart tidak sesuai / tidak lengkap')


class SparepartDataUpdateTestCase(APITestCase):

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

        # Setting up admin user and non-admin user
        self.role = Role.objects.create(name='Admin')
        self.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        self.extend_user = Extend_user.objects.create(user=self.user, role_id=self.role)
        self.client.force_authenticate(user=self.user)

        self.nonadmin_role = Role.objects.create(name='Karyawan')
        self.nonadmin_user = User.objects.create_user(username='Phalanx', password='TryintoTakeOver')
        self.extend_user = Extend_user.objects.create(user=self.nonadmin_user, role_id=self.nonadmin_role)

    def test_admin_update_sparepart_data_successfully(self) -> None:
        """
        Ensure admin can update sparepart data successfully
        """
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

    def test_nonlogin_user_cannot_update_sparepart_data(self) -> None:
        """
        Ensure non-login user cannot update sparepart data
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.sparepart_data_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_cannot_update_sparepart_data(self) -> None:
        """
        Ensure non-admin user cannot update sparepart data
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.put(self.sparepart_data_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_update_nonexist_sparepart_data(self) -> None:
        """
        Ensure admin cannot / Failed update non-exist sparepart data
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('sparepart_data_update', kwargs={'sparepart_id': 4563}),
                                   self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data sparepart tidak ditemukan')

    def test_admin_cannot_update_sparepart_with_empty_data(self) -> None:
        """
        Ensure admin cannot update data sparepart with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.sparepart_data_update_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data sparepart tidak sesuai / tidak lengkap')

    def test_admin_cannot_update_sparepart_with_partially_empty_data(self) -> None:
        """
        Ensure admin cannot update data sparepart with partially empty data / input
        """
        data = {'name': 'Razor Crest PF-0', 'partnumber': '127hash-19as88l0', 'quantity': 10}
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.sparepart_data_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data sparepart tidak sesuai / tidak lengkap')


class SparepartDataDeleteTestCase(APITestCase):
    def setUp(self) -> None:
        # Setting up sparepart data
        for i in range(5):
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

        # Setting up admin user and non-admin user
        self.role = Role.objects.create(name='Admin')
        self.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        self.extend_user = Extend_user.objects.create(user=self.user, role_id=self.role)
        self.client.force_authenticate(user=self.user)

        self.nonadmin_role = Role.objects.create(name='Karyawan')
        self.nonadmin_user = User.objects.create_user(username='Phalanx', password='TryintoTakeOver')
        self.extend_user = Extend_user.objects.create(user=self.nonadmin_user, role_id=self.nonadmin_role)

    def test_admin_delete_sparepart_data_successfully(self) -> None:
        """
        Ensure admin can delete sparepart data successfully
        """
        response = self.client.delete(self.sparepart_data_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data sparepart berhasil dihapus')

    def test_nonlogin_user_cannot_delete_sparepart_data(self) -> None:
        """
        Ensure non-login user cannot delete sparepart data
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.sparepart_data_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_cannot_delete_sparepart_data(self) -> None:
        """
        Ensure non-admin user cannot delete sparepart data
        """
        self.client.force_authenticate(user=self.nonadmin_user)
        response = self.client.delete(self.sparepart_data_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_cannot_delete_nonexist_sparepart_data(self) -> None:
        """
        Ensure admin cannot / failed to delete non-exist sparepart data
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('sparepart_data_delete', kwargs={'sparepart_id': 4563}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data sparepart tidak ditemukan')


class SalesListTestCase(APITestCase):
    sales_url = reverse('sales_list')

    def setUp(self) -> None:
        # Setting up admin user and non-admin user
        self.role = Role.objects.create(name='Admin')
        self.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        self.extend_user = Extend_user.objects.create(user=self.user, role_id=self.role)
        self.client.force_authenticate(user=self.user)

        self.nonadmin_role = Role.objects.create(name='Karyawan')
        self.nonadmin_user = User.objects.create_user(username='Phalanx', password='TryintoTakeOver')
        self.extend_user = Extend_user.objects.create(user=self.nonadmin_user, role_id=self.nonadmin_role)

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

        self.spareparts = Sparepart.objects.all()

        # Setting up sales data and getting their id
        for i in range(2):
            Sales.objects.create(
                customer_name='Brandon Sanderson',
                customer_contact='085456105311',
            )

        self.sales = Sales.objects.all()

        # Setting up sales detail data and getting their id
        Sales_detail.objects.create(
            quantity=2,
            is_grosir=False,
            sales_id=self.sales[0],
            sparepart_id=self.spareparts[3]
        )
        Sales_detail.objects.create(
            quantity=5,
            is_grosir=False,
            sales_id=self.sales[1],
            sparepart_id=self.spareparts[0]
        )
        Sales_detail.objects.create(
            quantity=3,
            is_grosir=False,
            sales_id=self.sales[1],
            sparepart_id=self.spareparts[1]
        )

        self.sales_details_id = [
            Sales_detail.objects.get(sparepart_id=self.spareparts[3].sparepart_id).sales_detail_id,
            Sales_detail.objects.get(sparepart_id=self.spareparts[0].sparepart_id).sales_detail_id,
            Sales_detail.objects.get(sparepart_id=self.spareparts[1].sparepart_id).sales_detail_id,
        ]

    def test_admin_successfully_access_sales_list(self) -> None:
        """
        Ensure admin can get sales list
        """
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
