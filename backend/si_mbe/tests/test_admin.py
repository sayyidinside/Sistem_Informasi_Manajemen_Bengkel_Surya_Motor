from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from si_mbe.models import (Brand, Profile, Restock, Restock_detail, Role,
                           Sales, Sales_detail, Sparepart, Storage, Supplier)


# Create your tests here.
class SetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and non-admin user
        cls.role = Role.objects.create(name='Admin')
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Profile.objects.create(user_id=cls.user, role_id=cls.role, name='Richard Rider')

        cls.owner_role = Role.objects.create(name='Pemilik')
        cls.owner = User.objects.create_user(username='worldmind', password='XandarianWorldmind')
        Profile.objects.create(user_id=cls.owner, role_id=cls.owner_role)

        return super().setUpTestData()


class AdminDashboardTestCase(SetTestCase):
    admin_dashboard_url = reverse('admin_dashboard')

    def test_admin_successfully_accessed_admin_dashboard(self) -> None:
        """
        Ensure admin can access admin dashboard
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nonlogin_user_failed_to_access_admin_dashboard(self) -> None:
        """
        Ensure non-login user cannot access admin dashboard
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_owner_failed_to_access_admin_dashboard(self) -> None:
        """
        Ensure non-admin user cannot access admin dashboard
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class SparepartDataListTestCase(SetTestCase):
    sparepart_data_list_url = reverse('sparepart_data_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up brand data
        cls.brand = Brand.objects.create(name='Kenshin')

        # Setting up storage data
        cls.storage = Storage.objects.create(
            code='6ABC',
            location='Rak Biru B6'
        )

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
                brand_id=cls.brand,
                storage_id=cls.storage
            )

        cls.sparepart = Sparepart.objects.all()

        return super().setUpTestData()

    def test_admin_successfully_access_sparepart_data_list(self) -> None:
        """
        Ensure admin can get sparepart data list successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.sparepart_data_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 3)
        self.assertEqual(response.data['results'], [
            {
                'sparepart_id': self.sparepart[0].sparepart_id,
                'name': self.sparepart[0].name,
                'partnumber': self.sparepart[0].partnumber,
                'quantity': self.sparepart[0].quantity,
                'motor_type': self.sparepart[0].motor_type,
                'sparepart_type': self.sparepart[0].sparepart_type,
                'brand': self.sparepart[0].brand_id.name,
                'price': str(self.sparepart[0].price),
                'grosir_price': str(self.sparepart[0].grosir_price),
                'location': self.storage.location
            },
            {
                'sparepart_id': self.sparepart[1].sparepart_id,
                'name': self.sparepart[1].name,
                'partnumber': self.sparepart[1].partnumber,
                'quantity': self.sparepart[1].quantity,
                'motor_type': self.sparepart[1].motor_type,
                'sparepart_type': self.sparepart[1].sparepart_type,
                'brand': self.sparepart[1].brand_id.name,
                'price': str(self.sparepart[1].price),
                'grosir_price': str(self.sparepart[1].grosir_price),
                'location': self.storage.location
            },
            {
                'sparepart_id': self.sparepart[2].sparepart_id,
                'name': self.sparepart[2].name,
                'partnumber': self.sparepart[2].partnumber,
                'quantity': self.sparepart[2].quantity,
                'motor_type': self.sparepart[2].motor_type,
                'sparepart_type': self.sparepart[2].sparepart_type,
                'brand': self.sparepart[2].brand_id.name,
                'price': str(self.sparepart[2].price),
                'grosir_price': str(self.sparepart[2].grosir_price),
                'location': self.storage.location
            }

        ])

    def test_nonlogin_user_failed_to_access_sparepart_data_list(self) -> None:
        """
        Ensure non-login user cannot access sparepart data list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.sparepart_data_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_owner_failed_to_access_sparepart_data_list(self) -> None:
        """
        Ensure non-admin user cannot access sparepart data list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.sparepart_data_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class SparepartDataAddTestCase(SetTestCase):
    sparepart_data_add_url = reverse('sparepart_data_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up brand data
        cls.brand = Brand.objects.create(name='Shimada')

        # Setting up storage data
        cls.storage = Storage.objects.create(
            code='6ABC',
            location='Rak Biru B6'
        )

        # Creating data that gonna be use as input
        cls.data_sparepart = {
            'name': 'Milano Buster T-194',
            'partnumber': '127hash-19as88l0',
            'quantity': 50,
            'motor_type': 'Yamaha Nmax',
            'sparepart_type': '24Q-22',
            'price': 5400000,
            'grosir_price': 5300000,
            'brand_id': cls.brand.brand_id,
            'storage_id': cls.storage.storage_id
        }

        return super().setUpTestData()

    def test_admin_successfully_add_new_sparepart_data(self) -> None:
        """
        Ensure admin can add new sparepart data successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.sparepart_data_add_url, self.data_sparepart)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Data sparepart berhasil ditambah')
        self.assertEqual(response.data['name'], self.data_sparepart['name'])
        self.assertEqual(response.data['partnumber'], self.data_sparepart['partnumber'])
        self.assertEqual(response.data['quantity'], self.data_sparepart['quantity'])
        self.assertEqual(response.data['motor_type'], self.data_sparepart['motor_type'])
        self.assertEqual(response.data['sparepart_type'], self.data_sparepart['sparepart_type'])
        self.assertEqual(response.data['brand_id'], self.data_sparepart['brand_id'])
        self.assertEqual(int(response.data['price']), self.data_sparepart['price'])
        self.assertEqual(int(response.data['grosir_price']), self.data_sparepart['grosir_price'])
        self.assertEqual(response.data['storage_id'], self.data_sparepart['storage_id'])

    def test_nonlogin_user_failed_to_add_new_sparepart_data(self) -> None:
        """
        Ensure non-login user cannot add new sparepart data
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.sparepart_data_add_url, self.data_sparepart)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_owner_failed_to_add_new_sparepart_data(self) -> None:
        """
        Ensure non-admin user cannot add new sparepart data
        """
        self.client.force_authenticate(user=self.owner)
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
        # Setting up brand data
        cls.brand = Brand.objects.create(name='Warbreaker')

        # Setting up storage data
        cls.storage = Storage.objects.create(
            code='6ABC',
            location='Rak Biru B6'
        )

        # Setting up new data to update sparepart data
        cls.data = {
            'name': 'Razor Crest PF-30',
            'partnumber': '7asAA-9293B',
            'quantity': 20,
            'motor_type': 'Navigations',
            'sparepart_type': '24Q-22',
            'price': 5800000,
            'grosir_price': 5400000,
            'brand_id': cls.brand.brand_id,
            'storage_id': cls.storage.storage_id
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
                brand_id=self.brand
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
        self.assertEqual(response.data['quantity'], self.data['quantity'])
        self.assertEqual(response.data['motor_type'], self.data['motor_type'])
        self.assertEqual(response.data['sparepart_type'], self.data['sparepart_type'])
        self.assertEqual(response.data['brand_id'], self.data['brand_id'])
        self.assertEqual(int(response.data['price']), self.data['price'])
        self.assertEqual(int(response.data['grosir_price']), self.data['grosir_price'])
        self.assertEqual(response.data['storage_id'], self.data['storage_id'])

    def test_nonlogin_user_failed_to_update_sparepart_data(self) -> None:
        """
        Ensure non-login user cannot update sparepart data
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.sparepart_data_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_owner_failed_to_update_sparepart_data(self) -> None:
        """
        Ensure non-admin user cannot update sparepart data
        """
        self.client.force_authenticate(user=self.owner)
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
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up brand data
        cls.brand = Brand.objects.create(name='Mistborn')

        return super().setUpTestData()

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
                brand_id=self.brand
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

    def test_owner_failed_to_delete_sparepart_data(self) -> None:
        """
        Ensure non-admin user cannot delete sparepart data
        """
        self.client.force_authenticate(user=self.owner)
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

    def test_owner_failed_to_access_sales_list(self) -> None:
        """
        Ensure non-admin user cannot access sales list
        """
        self.client.force_authenticate(user=self.owner)
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
        self.client.force_authenticate(user=self.owner)
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

    def test_owner_failed_to_update_sales(self) -> None:
        """
        Ensure non-admin user cannot update sales
        """
        self.client.force_authenticate(user=self.owner)
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

    def test_owner_failed_to_delete_sales(self) -> None:
        """
        Ensure non-admin user cannot delete sales
        """
        self.client.force_authenticate(user=self.owner)
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

    def test_owner_failed_to_access_restock_list(self) -> None:
        """
        Ensure non-admin user cannot access restock list
        """
        self.client.force_authenticate(user=self.owner)
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
        self.client.force_authenticate(user=self.owner)
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

    def test_owner_failed_to_update_restock(self) -> None:
        """
        Ensure non-admin user cannot update restock
        """
        self.client.force_authenticate(user=self.owner)
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

    def test_owner_failed_to_delete_restock(self) -> None:
        """
        Ensure non-admin user cannot delete restock
        """
        self.client.force_authenticate(user=self.owner)
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

    def test_owner_failed_to_access_supplier_list(self) -> None:
        """
        Ensure non-admin user cannot access supplier list
        """
        self.client.force_authenticate(user=self.owner)
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

    def test_owner_failed_to_add_new_supplier(self) -> None:
        """
        Ensure non-admin user cannot add new supplier
        """
        self.client.force_authenticate(user=self.owner)
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

    def test_owner_failed_to_update_supplier(self) -> None:
        """
        Ensure non-admin user cannot update supplier
        """
        self.client.force_authenticate(user=self.owner)
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

    def test_owner_failed_to_delete_supplier(self) -> None:
        """
        Ensure non-admin user cannot delete supplier
        """
        self.client.force_authenticate(user=self.owner)
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