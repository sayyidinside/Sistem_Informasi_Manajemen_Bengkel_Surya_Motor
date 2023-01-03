from datetime import date, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from si_mbe.models import (Brand, Category, Customer, Profile, Restock,
                           Restock_detail, Sales, Sales_detail, Salesman,
                           Service, Service_action, Service_sparepart,
                           Sparepart, Storage, Supplier, Mechanic)


# Create your tests here.
class SetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and non-admin user
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Profile.objects.create(user_id=cls.user, role='A', name='Richard Rider', contact='085260121548')

        cls.owner = User.objects.create_user(username='worldmind', password='XandarianWorldmind')
        Profile.objects.create(user_id=cls.owner, role='P', name='Nova Worldmind', contact='084086351044')

        return super().setUpTestData()


class AdminDashboardTestCase(SetTestCase):
    admin_dashboard_url = reverse('admin_dashboard')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up brand data
        cls.brand = Brand.objects.create(name='Marquet')

        # Setting up sparepart data
        cls.sparepart = []
        for i in range(11):
            cls.sparepart.append(
                Sparepart.objects.create(
                    name=f'Something {i}',
                    partnumber=f'HFh992-{i}',
                    quantity=50,
                    motor_type='Yamaha Nmax',
                    sparepart_type='24Q-22',
                    price=5400000,
                    workshop_price=5300000,
                    install_price=5500000,
                    limit=int(f'{i}1'),
                    brand_id=cls.brand
                )
            )

        # Setting up sales data
        cls.sales = Sales.objects.create(
            deposit=10000
        )

        # Setting up sales_detail data
        Sales_detail.objects.create(
            sales_id=cls.sales,
            sparepart_id=cls.sparepart[0],
            quantity=10
        )
        Sales_detail.objects.create(
            sales_id=cls.sales,
            sparepart_id=cls.sparepart[4],
            quantity=5
        )
        Sales_detail.objects.create(
            sales_id=cls.sales,
            sparepart_id=cls.sparepart[3],
            quantity=23
        )
        Sales_detail.objects.create(
            sales_id=cls.sales,
            sparepart_id=cls.sparepart[1],
            quantity=1
        )
        Sales_detail.objects.create(
            sales_id=cls.sales,
            sparepart_id=cls.sparepart[5],
            quantity=60
        )
        Sales_detail.objects.create(
            sales_id=cls.sales,
            sparepart_id=cls.sparepart[2],
            quantity=26
        )

        cls.restock = []
        # Setting up restock data
        for i in range(9):
            cls.restock.append(
                Restock.objects.create(
                    no_faktur=f'HF2-{i}',
                    due_date=date.today() + timedelta(days=i),
                    deposit=10000
                )
            )
        Restock.objects.create(
            no_faktur=f'HF2-{i}',
            due_date=date.today() + timedelta(days=i),
            deposit=10000,
            is_paid_off=True
        )

        for i in range(9):
            Restock_detail.objects.create(
                restock_id=cls.restock[i],
                sparepart_id=cls.sparepart[i],
                individual_price=int(f'{i}20000'),
                quantity=11+i
            )

        # Setting up service
        cls.service = Service.objects.create(
            police_number='B 23 A',
            motor_type='C',
            discount=0
        )

        # Setting up service_sparepart
        Service_sparepart.objects.create(
            service_id=cls.service,
            sparepart_id=cls.sparepart[0],
            quantity=12
        )
        Service_sparepart.objects.create(
            service_id=cls.service,
            sparepart_id=cls.sparepart[3],
            quantity=31
        )
        Service_sparepart.objects.create(
            service_id=cls.service,
            sparepart_id=cls.sparepart[1],
            quantity=28
        )
        Service_sparepart.objects.create(
            service_id=cls.service,
            sparepart_id=cls.sparepart[2],
            quantity=8
        )
        Service_sparepart.objects.create(
            service_id=cls.service,
            sparepart_id=cls.sparepart[5],
            quantity=13
        )
        Service_sparepart.objects.create(
            service_id=cls.service,
            sparepart_id=cls.sparepart[6],
            quantity=21
        )
        return super().setUpTestData()

    def test_admin_successfully_accessed_admin_dashboard(self) -> None:
        """
        Ensure admin can access admin dashboard
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['sparepart_on_limit']), 6)
        self.assertEqual(len(response.data['restock_due']), 8)
        self.assertEqual(len(response.data['most_sold']), 10)
        self.assertEqual(len(response.data['most_used']), 10)

    def test_nonlogin_user_failed_to_access_admin_dashboard(self) -> None:
        """
        Ensure non-login user cannot access admin dashboard
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_admin_dashboard(self) -> None:
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
            code='AD-34',
        )

        # Setting up category data
        cls.category = Category.objects.create(name='Add-On')

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
                workshop_price=5300000,
                install_price=5500000,
                brand_id=cls.brand,
                storage_id=cls.storage,
                category_id=cls.category
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
                'partnumber': self.sparepart[0].partnumber,
                'name': self.sparepart[0].name,
                'brand': self.sparepart[0].brand_id.name,
                'category': self.sparepart[0].category_id.name,
                'quantity': self.sparepart[0].quantity,
            },
            {
                'sparepart_id': self.sparepart[1].sparepart_id,
                'partnumber': self.sparepart[1].partnumber,
                'name': self.sparepart[1].name,
                'brand': self.sparepart[1].brand_id.name,
                'category': self.sparepart[1].category_id.name,
                'quantity': self.sparepart[1].quantity,
            },
            {
                'sparepart_id': self.sparepart[2].sparepart_id,
                'partnumber': self.sparepart[2].partnumber,
                'name': self.sparepart[2].name,
                'brand': self.sparepart[2].brand_id.name,
                'category': self.sparepart[2].category_id.name,
                'quantity': self.sparepart[2].quantity,
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

    def test_nonadmin_user_failed_to_access_sparepart_data_list(self) -> None:
        """
        Ensure non-admin user cannot access sparepart data list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.sparepart_data_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_successfully_searching_sparepart_with_result(self) -> None:
        """
        Ensure admin who searching sparepart with correct keyword get correct result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('sparepart_data_list') + f'?q={self.sparepart[1].name}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['results'], [
            {
                'sparepart_id': self.sparepart[1].sparepart_id,
                'partnumber': self.sparepart[1].partnumber,
                'name': self.sparepart[1].name,
                'brand': self.sparepart[1].brand_id.name,
                'category': self.sparepart[1].category_id.name,
                'quantity': self.sparepart[1].quantity,
            }
        ])

    def test_admin_successfully_searching_sparepart_without_result(self) -> None:
        """
        Ensure admin search sparepart that doesn't exist get empty result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('sparepart_data_list') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 0)
        self.assertEqual(response.data['message'], 'Sparepart yang dicari tidak ditemukan')


class SparepartDataAddTestCase(SetTestCase):
    sparepart_data_add_url = reverse('sparepart_data_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up brand data
        cls.brand = Brand.objects.create(name='Shimada')

        # Setting up storage data
        cls.storage = Storage.objects.create(code='JKG-299')

        # Setting up category data
        cls.category = Category.objects.create(name='Engine')

        # Creating data that gonna be use as input
        cls.data_sparepart = {
            'name': 'Milano Buster T-194',
            'partnumber': '127hash-19as88l0',
            'quantity': 50,
            'motor_type': 'Yamaha Nmax',
            'sparepart_type': '24Q-22',
            'price': 5400000,
            'workshop_price': 5300000,
            'install_price': 5500000,
            'brand_id': cls.brand.brand_id,
            'storage_id': cls.storage.storage_id,
            'category_id': cls.category.category_id,
            'image': ''
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
        self.assertEqual(int(response.data['workshop_price']), self.data_sparepart['workshop_price'])
        self.assertEqual(int(response.data['install_price']), self.data_sparepart['install_price'])
        self.assertEqual(response.data['storage_id'], self.data_sparepart['storage_id'])
        self.assertEqual(response.data['category_id'], self.data_sparepart['category_id'])
        self.assertEqual(response.data['image'], None)

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

        # Setting up category
        cls.category = Category.objects.create(name='Pathfinder')

        # Setting up new data to update sparepart data
        cls.data = {
            'name': 'Razor Crest PF-30',
            'partnumber': '7asAA-9293B',
            'quantity': 20,
            'category_id': cls.category.category_id,
            'motor_type': 'Spase Ship',
            'sparepart_type': '24Q-22',
            'brand_id': cls.brand.brand_id,
            'price': 5800000,
            'workshop_price': 5400000,
            'install_price': 5500000,
            'storage_id': cls.storage.storage_id,
            'image': ''
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
                workshop_price=5400000,
                install_price=5500000,
                brand_id=self.brand,
                category_id=self.category
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
        self.assertEqual(int(response.data['workshop_price']), self.data['workshop_price'])
        self.assertEqual(int(response.data['install_price']), self.data['install_price'])
        self.assertEqual(response.data['storage_id'], self.data['storage_id'])
        self.assertEqual(response.data['category_id'], self.data['category_id'])
        self.assertEqual(response.data['image'], None)

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
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.sparepart_data_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_update_nonexist_sparepart_data(self) -> None:
        """
        Ensure admin cannot / Failed update non-exist sparepart data
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('sparepart_data_update', kwargs={'sparepart_id': 45631}),
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

        # Setting up category data
        cls.category = Category.objects.create(name='Storage')

        # Setting up storage data
        cls.storage = Storage.objects.create(code='AP-20')

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
                workshop_price=750000,
                install_price=850000,
                brand_id=self.brand,
                category_id=self.category,
                storage_id=self.storage
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
        # Setting up category
        cls.category = Category.objects.create(name='Transform Device')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Nein')

        # Setting up sparepart data and getting their id
        for i in range(5):
            Sparepart.objects.create(
                name=f'Gaia Memory D-9-2{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Fuuto Wind',
                sparepart_type='USB',
                price=5400000,
                workshop_price=5300000,
                install_price=5500000,
                brand_id=cls.brand,
                category_id=cls.category
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up customer
        cls.customer = Customer.objects.create(
            name='Brandon Sanderson',
            contact='085456105311'
        )

        # Setting up sales data and getting their id
        for i in range(2):
            Sales.objects.create(
                customer_id=cls.customer
            )

        cls.sales = Sales.objects.all()

        # Setting up sales detail data and getting their id
        cls.sales_details_1 = Sales_detail.objects.create(
            quantity=2,
            is_workshop=False,
            sales_id=cls.sales[0],
            sparepart_id=cls.spareparts[3]
        )
        cls.sales_details_2 = Sales_detail.objects.create(
            quantity=5,
            is_workshop=True,
            sales_id=cls.sales[1],
            sparepart_id=cls.spareparts[0]
        )
        cls.sales_details_3 = Sales_detail.objects.create(
            quantity=3,
            is_workshop=False,
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
                'customer': self.sales[0].customer_id.name,
                'contact': self.sales[0].customer_id.contact,
                'total_price_sales': 10800000,
                'is_paid_off': False,
                'deposit': str(self.sales[0].deposit),
                'content': [
                    {
                        'sales_detail_id': self.sales_details_1.sales_detail_id,
                        'sparepart': self.spareparts[3].name,
                        'quantity': 2,
                        'is_workshop': False,
                        'total_price': 10800000
                    }
                ]
            },
            {
                'sales_id': self.sales[1].sales_id,
                'customer': self.sales[1].customer_id.name,
                'contact': self.sales[1].customer_id.contact,
                'total_price_sales': 42700000,
                'is_paid_off': False,
                'deposit': str(self.sales[1].deposit),
                'content': [
                    {
                        'sales_detail_id': self.sales_details_2.sales_detail_id,
                        'sparepart': self.spareparts[0].name,
                        'quantity': 5,
                        'is_workshop': True,
                        'total_price': 26500000
                    },
                    {
                        'sales_detail_id': self.sales_details_3.sales_detail_id,
                        'sparepart': self.spareparts[1].name,
                        'quantity': 3,
                        'is_workshop': False,
                        'total_price': 16200000
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
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.sales_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class SalesAddTestCase(SetTestCase):
    sales_add_url = reverse('sales_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up storage data
        cls.storage = Storage.objects.create(code='GA-9')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Stark Industries')

        # Setting up category data
        cls.category = Category.objects.create(name='Fuel')

        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'Core Fluid P-{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Queen Jet',
                sparepart_type='Oil',
                price=5400000,
                workshop_price=5300000,
                install_price=5500000,
                brand_id=cls.brand,
                storage_id=cls.storage,
                category_id=cls.category
            )

        cls.spareparts = Sparepart.objects.all().order_by('sparepart_id')

        # Setting up customer data
        cls.customer = Customer.objects.create(
            name='Fjord',
            contact='084531584533'
        )

        # Creating data that gonna be use as input
        cls.data = {
            'customer_id': cls.customer.customer_id,
            'is_paid_off': False,
            'deposit': 200000,
            'content': [
                {
                    'sparepart_id': cls.spareparts[1].sparepart_id,
                    'quantity': 1,
                    'is_workshop': False,
                },
                {
                    'sparepart_id': cls.spareparts[0].sparepart_id,
                    'quantity': 30,
                    'is_workshop': True,
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
        self.assertEqual(response.data['customer_id'], self.customer.customer_id)
        self.assertEqual(response.data['is_paid_off'], self.data['is_paid_off'])
        self.assertEqual(int(response.data['deposit']), self.data['deposit'])
        self.assertEqual(len(response.data['content']), 2)
        self.assertEqual(response.data['content'][0]['sparepart_id'], self.spareparts[1].sparepart_id)
        self.assertEqual(response.data['content'][0]['quantity'], 1)
        self.assertEqual(response.data['content'][0]['is_workshop'], False)

        # ensure sparepart quantity will be subtracted by detail's quantity
        # after sales successfully added
        self.assertEqual(self.spareparts[0].quantity, 20)
        self.assertEqual(self.spareparts[1].quantity, 49)

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
        # Setting up storage data
        cls.storage = Storage.objects.create(code='DG-001')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Doom Guys')

        # Setting up category data
        cls.category = Category.objects.create(name='Weapon')

        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'B-F-Gun {i}',
                partnumber=f'JKL03uf-U-{i}',
                quantity=int(f'5{i}'),
                motor_type='Dreadnought',
                sparepart_type='Barrel',
                price=105000,
                workshop_price=100000,
                install_price=110000,
                brand_id=cls.brand,
                storage_id=cls.storage,
                category_id=cls.category
            )

        cls.spareparts = Sparepart.objects.all().order_by('sparepart_id')

        # Setting up customer data
        cls.customer = Customer.objects.create(
            name='Clem Andor',
            contact='085425502660'
        )

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up sales data and getting their id
        self.sales = Sales.objects.create(
            customer_id=self.customer
        )

        # Getting newly added sales it's sales_id then set it to kwargs in reverse url
        self.sales_update_url = reverse('sales_update', kwargs={'sales_id': self.sales.sales_id})

        # Setting up sales detail data and getting their id
        self.sales_detail_1 = Sales_detail.objects.create(
            quantity=2,
            is_workshop=False,
            sales_id=self.sales,
            sparepart_id=self.spareparts[2]
        )
        self.sales_detail_2 = Sales_detail.objects.create(
            quantity=35,
            is_workshop=True,
            sales_id=self.sales,
            sparepart_id=self.spareparts[0]
        )

        # Creating data that gonna be use as input
        self.data = {
            'customer_id': self.customer.customer_id,
            'is_paid_off': True,
            'deposit': 5000000,
            'content': [
                {
                    'sales_detail_id': self.sales_detail_1.sales_detail_id,
                    'sparepart_id': self.spareparts[2].sparepart_id,
                    'quantity': 5,
                    'is_workshop': False,
                },
                {
                    'sales_detail_id': self.sales_detail_2.sales_detail_id,
                    'sparepart_id': self.spareparts[0].sparepart_id,
                    'quantity': 30,
                    'is_workshop': True,
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
        self.assertEqual(response.data['customer_id'], self.customer.customer_id)
        self.assertEqual(response.data['is_paid_off'], self.data['is_paid_off'])
        self.assertEqual(int(response.data['deposit']), self.data['deposit'])
        self.assertEqual(len(response.data['content']), 2)
        self.assertEqual(response.data['content'][0]['sparepart_id'], self.spareparts[2].sparepart_id)
        self.assertEqual(response.data['content'][0]['quantity'], 5)
        self.assertEqual(response.data['content'][0]['is_workshop'], False)
        self.assertEqual(response.data['content'][1]['sparepart_id'], self.spareparts[0].sparepart_id)
        self.assertEqual(response.data['content'][1]['quantity'], 30)
        self.assertEqual(response.data['content'][1]['is_workshop'], True)

        # ensure sparepart quantity will be subtracted by detail's quantity
        # after sales successfully updated
        self.assertEqual(self.spareparts[0].quantity, 55)
        self.assertEqual(self.spareparts[2].quantity, 49)

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
        # Setting up storage data
        cls.storage = Storage.objects.create(code='DG-001')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Doom Guys')

        # Setting up category data
        cls.category = Category.objects.create(name='Weapon')

        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'spelljammer {i}L-1',
                partnumber=f'J8OI0-h8{i}',
                quantity=int(f'7{i}'),
                motor_type='Space Ship',
                sparepart_type='Core',
                price=105000,
                workshop_price=100000,
                install_price=110000,
                brand_id=cls.brand,
                category_id=cls.category,
                storage_id=cls.storage
            )

        cls.spareparts = Sparepart.objects.all().order_by('sparepart_id')

        # Setting up customer data
        cls.customer = Customer.objects.create(
            name='Zurat Gracdion',
            contact='085425045263'
        )

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up sales data and getting their id
        self.sales = Sales.objects.create(
            customer_id=self.customer,
            deposit=400000,
        )

        # Getting newly added sales it's sales_id then set it to kwargs in reverse url
        self.sales_delete_url = reverse('sales_delete', kwargs={'sales_id': self.sales.sales_id})

        # Setting up sales detail data
        Sales_detail.objects.create(
            quantity=3,
            is_workshop=False,
            sales_id=self.sales,
            sparepart_id=self.spareparts[2]
        )
        Sales_detail.objects.create(
            quantity=51,
            is_workshop=True,
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

        # ensure sparepart quantity will be added by detail's quantity
        # after sales successfully deleted
        self.assertEqual(self.spareparts[0].quantity, 121)
        self.assertEqual(self.spareparts[2].quantity, 75)

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
            contact='084894564563',
            rekening_number='98186046800001',
            rekening_name='Saburo Arasaka',
            rekening_bank='Bank Night City'
        )

        # Setting up salesman data
        cls.salesman = Salesman.objects.create(
            supplier_id=cls.supplier,
            name='Saburo Arasaka',
            contact='084523015663'
        )

        # Setting up storage data
        cls.storage = Storage.objects.create(code='CP-77')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Arasaka')

        # Setting up category data
        cls.category = Category.objects.create(name='Cyberware')

        # Setting up sparepart data and getting their id
        for i in range(4):
            Sparepart.objects.create(
                name=f'Sandevistan PV-{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Cyberpunk',
                sparepart_type='Back Body',
                price=4700000,
                workshop_price=4620000,
                install_price=4830000,
                brand_id=cls.brand,
                storage_id=cls.storage,
                category_id=cls.category
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up restock data and getting their object
        for i in range(2):
            Restock.objects.create(
                no_faktur=f'URH45/28394/2022-N{i}D',
                due_date=date(2023, 4, 13),
                is_paid_off=False,
                salesman_id=cls.salesman
            )

        cls.restocks = Restock.objects.all().order_by('restock_id')

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

        # Validating surface level information of restock
        # The first result data
        self.assertEqual(response.data['results'][0]['restock_id'], self.restocks[0].restock_id)
        self.assertEqual(response.data['results'][0]['no_faktur'], self.restocks[0].no_faktur)
        self.assertEqual(response.data['results'][0]['created_at'],
                         (self.restocks[0].created_at + timedelta(hours=7)).strftime('%d-%m-%Y %H:%M:%S'))
        self.assertEqual(response.data['results'][0]['supplier'], self.supplier.name)
        self.assertEqual(response.data['results'][0]['total_restock_cost'], 9100000)
        self.assertEqual(response.data['results'][0]['is_paid_off'], self.restocks[0].is_paid_off)
        # The second result data
        self.assertEqual(response.data['results'][1]['restock_id'], self.restocks[1].restock_id)
        self.assertEqual(response.data['results'][1]['no_faktur'], self.restocks[1].no_faktur)
        self.assertEqual(response.data['results'][1]['created_at'],
                         (self.restocks[1].created_at + timedelta(hours=7)).strftime('%d-%m-%Y %H:%M:%S'))
        self.assertEqual(response.data['results'][1]['supplier'], self.supplier.name)
        self.assertEqual(response.data['results'][1]['total_restock_cost'], 36400000)
        self.assertEqual(response.data['results'][1]['is_paid_off'], self.restocks[1].is_paid_off)

        # Validating detail information per sparepart of restock in content field
        # The first result data
        self.assertEqual(response.data['results'][0]['content'][0]['restock_detail_id'],
                         self.restock_detail_1.restock_detail_id)
        self.assertEqual(response.data['results'][0]['content'][0]['sparepart'],
                         self.spareparts[3].name)
        self.assertEqual(response.data['results'][0]['content'][0]['individual_price'],
                         str(4550000))
        self.assertEqual(response.data['results'][0]['content'][0]['quantity'],
                         2)
        self.assertEqual(response.data['results'][0]['content'][0]['total_price'],
                         9100000)
        # The second result data
        self.assertEqual(response.data['results'][1]['content'][0]['restock_detail_id'],
                         self.restock_detail_2.restock_detail_id)
        self.assertEqual(response.data['results'][1]['content'][0]['sparepart'],
                         self.spareparts[0].name)
        self.assertEqual(response.data['results'][1]['content'][0]['individual_price'],
                         str(4550000))
        self.assertEqual(response.data['results'][1]['content'][0]['quantity'],
                         5)
        self.assertEqual(response.data['results'][1]['content'][0]['total_price'],
                         22750000)
        self.assertEqual(response.data['results'][1]['content'][1]['restock_detail_id'],
                         self.restock_detail_3.restock_detail_id)
        self.assertEqual(response.data['results'][1]['content'][1]['sparepart'],
                         self.spareparts[1].name)
        self.assertEqual(response.data['results'][1]['content'][1]['individual_price'],
                         str(4550000))
        self.assertEqual(response.data['results'][1]['content'][1]['quantity'],
                         3)
        self.assertEqual(response.data['results'][1]['content'][1]['total_price'],
                         13650000)

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
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.restock_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_successfully_searching_restock_with_result(self) -> None:
        """
        Ensure admin who searching restock with correct keyword get correct result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('restock_list') + f'?q={self.restocks[0].no_faktur}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['results'][0]['restock_id'], self.restocks[0].restock_id)
        self.assertEqual(response.data['results'][0]['no_faktur'], self.restocks[0].no_faktur)
        self.assertEqual(response.data['results'][0]['created_at'],
                         (self.restocks[0].created_at + timedelta(hours=7)).strftime('%d-%m-%Y %H:%M:%S'))
        self.assertEqual(response.data['results'][0]['supplier'], self.supplier.name)
        self.assertEqual(response.data['results'][0]['total_restock_cost'], 9100000)
        self.assertEqual(response.data['results'][0]['is_paid_off'], self.restocks[0].is_paid_off)

    def test_admin_successfully_searching_restock_without_result(self) -> None:
        """
        Ensure admin search restock that doesn't exist get empty result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('restock_list') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['count_item'], 0)
        self.assertEqual(response.data['message'], 'Pengadaan / restock yang dicari tidak ditemukan')


class RestockAddTestCase(SetTestCase):
    restock_add_url = reverse('restock_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up supplier
        cls.supplier = Supplier.objects.create(
            name='Parker Industries',
            contact='084526301053',
            rekening_number='98186046800001',
            rekening_name='Peter Parker',
            rekening_bank='Bank DMG'
        )

        # Setting up salesman data
        cls.salesman = Salesman.objects.create(
            supplier_id=cls.supplier,
            name='Peter Parker',
            contact='084105634154'
        )

        # Setting up storage data
        cls.storage = Storage.objects.create(code='SP-31')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Parker')

        # Setting up category data
        cls.category = Category.objects.create(name='Accessories')

        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'Webware V.{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Wrist Device',
                sparepart_type='Braclet',
                price=5400000,
                workshop_price=5300000,
                install_price=5500000,
                brand_id=cls.brand,
                category_id=cls.category,
                storage_id=cls.storage
            )

        cls.spareparts = Sparepart.objects.all().order_by('sparepart_id')

        # Creating data that gonna be use as input
        cls.data = {
            'no_faktur': 'URH45/28394/2022-N1D',
            'due_date': date(2023, 4, 13),
            'salesman_id': cls.salesman.salesman_id,
            'deposit': 500000000,
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

        # Validating surface level information of restock
        self.assertEqual(response.data['no_faktur'], self.data['no_faktur'])
        self.assertEqual(response.data['due_date'], self.data['due_date'].strftime('%d-%m-%Y'))
        self.assertEqual(response.data['salesman_id'], self.salesman.salesman_id)
        self.assertEqual(response.data['supplier'], self.salesman.supplier_id.name)
        self.assertEqual(response.data['total_sparepart_quantity'], 210)
        self.assertEqual(response.data['total_restock_cost'], 915000000)
        self.assertEqual(int(response.data['deposit']), self.data['deposit'])
        self.assertEqual(response.data['remaining_payment'], 415000000)
        self.assertEqual(response.data['is_paid_off'], False)
        self.assertEqual(len(response.data['content']), 2)

        # Validating detail information per sparepart of restock in content field
        self.assertEqual(response.data['content'][0]['sparepart_id'], self.spareparts[0].sparepart_id)
        self.assertEqual(response.data['content'][0]['individual_price'],
                         str(self.data['content'][0]['individual_price']))
        self.assertEqual(response.data['content'][0]['quantity'], self.data['content'][0]['quantity'])
        self.assertEqual(response.data['content'][0]['sub_total'], 705000000)
        self.assertEqual(response.data['content'][1]['sparepart_id'], self.spareparts[1].sparepart_id)
        self.assertEqual(response.data['content'][1]['individual_price'],
                         str(self.data['content'][1]['individual_price']))
        self.assertEqual(response.data['content'][1]['quantity'], self.data['content'][1]['quantity'])
        self.assertEqual(response.data['content'][1]['sub_total'], 210000000)

        # ensure sparepart quantity will be added (+) by detail's quantity
        # after restock successfully added
        self.assertEqual(self.spareparts[0].quantity, 200)
        self.assertEqual(self.spareparts[1].quantity, 110)

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
            contact='084526301053',
            rekening_number='8468464056156',
            rekening_name='Pumat Sol',
            rekening_bank='Bank Zadash'
        )

        # Setting up salesman data
        cls.salesman = Salesman.objects.create(
            supplier_id=cls.supplier,
            name='Pumat Sol',
            contact='084105634154'
        )

        # Setting up storage data
        cls.storage = Storage.objects.create(code='P-3')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Cerbereus')

        # Setting up category data
        cls.category = Category.objects.create(name='Potion')

        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'Potion of Haste +{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=100,
                motor_type='Adventurer',
                sparepart_type='Buff',
                price=5400000,
                workshop_price=5300000,
                install_price=5500000,
                brand_id=None
            )

        cls.spareparts = Sparepart.objects.all().order_by('sparepart_id')

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up restock detail data
        self.restock = Restock.objects.create(
                no_faktur='78SDFBH/2022-YE/FA89',
                due_date=date(2023, 4, 13),
                salesman_id=self.salesman,
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
            'salesman_id': self.salesman.salesman_id,
            'deposit': 802750000,
            'content': [
                {
                    'restock_detail_id': self.restock_detail_1.restock_detail_id,
                    'sparepart_id': self.spareparts[0].sparepart_id,
                    'individual_price':4550000,
                    'quantity': 170,
                },
                {
                    'restock_detail_id': self.restock_detail_2.restock_detail_id,
                    'sparepart_id': self.spareparts[1].sparepart_id,
                    'individual_price':450000,
                    'quantity': 65,
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

        # Validating surface level information of restock
        self.assertEqual(response.data['no_faktur'], self.data['no_faktur'])
        self.assertEqual(response.data['due_date'], self.data['due_date'].strftime('%d-%m-%Y'))
        self.assertEqual(response.data['salesman_id'], self.salesman.salesman_id)
        self.assertEqual(response.data['supplier'], self.salesman.supplier_id.name)
        self.assertEqual(response.data['total_sparepart_quantity'], 235)
        self.assertEqual(response.data['total_restock_cost'], 802750000)
        self.assertEqual(int(response.data['deposit']), self.data['deposit'])
        self.assertEqual(response.data['remaining_payment'], 0)
        self.assertEqual(response.data['is_paid_off'], True)
        self.assertEqual(len(response.data['content']), 2)

        # Validating detail information per sparepart of restock in content field
        self.assertEqual(response.data['content'][0]['restock_detail_id'], self.restock_detail_1.restock_detail_id)
        self.assertEqual(response.data['content'][0]['sparepart_id'], self.spareparts[0].sparepart_id)
        self.assertEqual(response.data['content'][0]['individual_price'],
                         str(self.data['content'][0]['individual_price']))
        self.assertEqual(response.data['content'][0]['quantity'], self.data['content'][0]['quantity'])
        self.assertEqual(response.data['content'][0]['sub_total'], 773500000)
        self.assertEqual(response.data['content'][1]['restock_detail_id'], self.restock_detail_2.restock_detail_id)
        self.assertEqual(response.data['content'][1]['sparepart_id'], self.spareparts[1].sparepart_id)
        self.assertEqual(response.data['content'][1]['individual_price'],
                         str(self.data['content'][1]['individual_price']))
        self.assertEqual(response.data['content'][1]['quantity'], self.data['content'][1]['quantity'])
        self.assertEqual(response.data['content'][1]['sub_total'], 29250000)

        # ensure sparepart quantity will be added (+) by detail's quantity
        # after restock successfully updated
        self.assertEqual(self.spareparts[0].quantity, 70)
        self.assertEqual(self.spareparts[1].quantity, 115)

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
            contact='084526301053',
            rekening_number='8468464056156',
            rekening_name='Susan Storm',
            rekening_bank='Bank Baxter'
        )

        # Setting up salesman data
        cls.salesman = Salesman.objects.create(
            supplier_id=cls.supplier,
            name='Reed Richards',
            contact='084105634154'
        )

        # Setting up storage data
        cls.storage = Storage.objects.create(code='FF-31')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Baster Creation')

        # Setting up category data
        cls.category = Category.objects.create(name='Debuff')

        # Setting up sparepart data and getting their id
        for i in range(3):
            Sparepart.objects.create(
                name=f'Ultimate Nulifier {i}',
                partnumber=f'J8OI0-h8{i}',
                quantity=int(f'37{i}'),
                motor_type='Inventions',
                sparepart_type='Device',
                price=105000,
                workshop_price=100000,
                install_price=110000,
                brand_id=cls.brand,
                category_id=cls.category,
                storage_id=cls.storage
            )

        cls.spareparts = Sparepart.objects.all().order_by('sparepart_id')

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up restock detail data
        self.restock = Restock.objects.create(
                no_faktur='78SDFBH/2022-YE/FA89',
                due_date=date(2023, 4, 13),
                salesman_id=self.salesman,
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
        self.assertEqual(Restock.objects.count(), 0)
        self.assertEqual(Restock_detail.objects.count(), 0)

        # ensure sparepart quantity will be subtracted by detail's quantity
        # after restock successfully delete
        self.assertEqual(self.spareparts[0].quantity, 170)
        self.assertEqual(self.spareparts[1].quantity, 321)

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
        cls.supplier = Supplier.objects.create(
            name='Alpha Flight',
            contact='088464105635',
        )
        Supplier.objects.create(
            name='New Warriors',
            contact='084108910563',
        )
        Supplier.objects.create(
            name='Quite Council',
            contact='089661056345',
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
        self.assertEqual(response.data['results'][0]['name'], 'Alpha Flight')
        self.assertEqual(response.data['results'][0]['contact'], '088464105635')
        self.assertEqual(response.data['results'][1]['name'], 'New Warriors')
        self.assertEqual(response.data['results'][1]['contact'], '084108910563')
        self.assertEqual(response.data['results'][2]['name'], 'Quite Council')
        self.assertEqual(response.data['results'][2]['contact'], '089661056345')

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
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.supplier_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_successfully_searching_supplier_with_result(self) -> None:
        """
        Ensure admin who searching supplier with correct keyword get correct result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('supplier_list') + f'?q={self.supplier.name}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['results'], [
            {
                'supplier_id': self.supplier.supplier_id,
                'name': self.supplier.name,
                'contact': self.supplier.contact,
            }
        ])

    def test_admin_successfully_searching_supplier_without_result(self) -> None:
        """
        Ensure admin search supplier that doesn't exist get empty result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('supplier_list') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 0)
        self.assertEqual(response.data['message'], 'Supplier yang dicari tidak ditemukan')


class SupplierAddTestCase(SetTestCase):
    supplier_add_url = reverse('supplier_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Creating data that gonna be use as input
        cls.data = {
            'name': 'Mighty Nein',
            'contact': '084110864563',
            'rekening_number': '468408644866',
            'rekening_name': 'Fellowship',
            'rekening_bank': 'Bank Power Metal'
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
        self.assertEqual(response.data['contact'], self.data['contact'])
        self.assertEqual(response.data['rekening_number'], self.data['rekening_number'])
        self.assertEqual(response.data['rekening_name'], self.data['rekening_name'])
        self.assertEqual(response.data['rekening_bank'], self.data['rekening_bank'])

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
            'contact': '081526210523',
            'rekening_number': '5408654681531',
            'rekening_name': 'Charge Blade User',
            'rekening_bank': 'Bank Astera'
        }

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up supplier
        self.supplier = Supplier.objects.create(
            name='Yukumo',
            contact='084108910563',
            rekening_number='540006445154',
            rekening_name='Dual Blade User',
            rekening_bank='Bank Seliana'
        )

        self.supplier_update_url = reverse('supplier_update', kwargs={'supplier_id': self.supplier.supplier_id})

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
        self.assertEqual(response.data['contact'], self.data['contact'])
        self.assertEqual(response.data['rekening_number'], self.data['rekening_number'])
        self.assertEqual(response.data['rekening_name'], self.data['rekening_name'])
        self.assertEqual(response.data['rekening_bank'], self.data['rekening_bank'])

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
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.supplier_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_update_nonexist_supplier(self) -> None:
        """
        Ensure admin cannot update non-exist supplier
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('supplier_update', kwargs={'supplier_id': 526523}),
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
            contact='088464105635',
            rekening_number='98186046800001',
            rekening_name='Jack Morrison',
            rekening_bank='Bank Blackwatch'
        )
        cls.supplier_2 = Supplier.objects.create(
            name='Null Sector',
            contact='084108910563',
            rekening_number='8648646804601',
            rekening_name='Ramattra',
            rekening_bank='Bank Nemesis'
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


class ServiceListTestCase(SetTestCase):
    service_list_url = reverse('service_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up additional admin data
        cls.admin = User.objects.create_user(
            username='greg',
            password='GregTheGarlicFarmer',
            email='greg@skycraft.com'
        )
        Profile.objects.create(
            user_id=cls.admin,
            role='A',
            name='Greg',
            contact='081086016510',
            address='Honeywood'
        )

        # Setting up mechanic data
        cls.mechanic = Mechanic.objects.create(
            name='Bodger Bloger',
            contact='086206164404',
            address='Honeywood'
        )

        # Setting up customer data
        cls.customer_1 = Customer.objects.create(
            name='Bartholomew Osiris Bladesong',
            contact='082541684051',
        )
        cls.customer_2 = Customer.objects.create(
            name='Baradun',
            contact='082541684051',
        )

        cls.service_1 = Service.objects.create(
            police_number='B 1293 A',
            motor_type='Beneli',
            deposit=500000,
            discount=20000,
            user_id=cls.admin,
            mechanic_id=cls.mechanic,
            customer_id=cls.customer_1
        )

        cls.service_2 = Service.objects.create(
            police_number='B 4   CA',
            motor_type='Kymco',
            deposit=40000,
            discount=5000,
            user_id=cls.admin,
            mechanic_id=cls.mechanic,
            customer_id=cls.customer_2
        )

        # Setting up service actions
        cls.action_1 = Service_action.objects.create(
            name='Pompa Ban',
            cost='10000',
            service_id=cls.service_1
        )
        cls.action_2 = Service_action.objects.create(
            name='Bongkar Mesin',
            cost='400000',
            service_id=cls.service_1
        )
        cls.action_3 = Service_action.objects.create(
            name='Angkat Lampu',
            cost='300000',
            service_id=cls.service_1
        )

        # Setting up storage data
        cls.storage = Storage.objects.create(code='MN-9')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Lavish Chateau')

        # Setting up category data
        cls.category = Category.objects.create(name='Food')

        # Setting up sparepart data
        cls.sparepart_1 = Sparepart.objects.create(
            name='Chorcoal Cupcake',
            partnumber='JFLJ23-Aj',
            quantity=50,
            motor_type='Human',
            sparepart_type='Spices',
            price=105000,
            workshop_price=100000,
            install_price=110000,
            brand_id=cls.brand,
            category_id=cls.category,
            storage_id=cls.storage
        )
        cls.sparepart_2 = Sparepart.objects.create(
            name='Dead People Tea',
            partnumber='HF9912-2',
            quantity=35,
            motor_type='Human',
            sparepart_type='Tea Leaf',
            price=75000,
            workshop_price=70000,
            install_price=80000,
            brand_id=cls.brand,
            category_id=cls.category,
            storage_id=cls.storage
        )

        # Setting up service sparepart
        cls.service_sparepart_1 = Service_sparepart.objects.create(
            quantity=2,
            service_id=cls.service_1,
            sparepart_id=cls.sparepart_1
        )
        cls.service_sparepart_2 = Service_sparepart.objects.create(
            quantity=3,
            service_id=cls.service_2,
            sparepart_id=cls.sparepart_1
        )
        cls.service_sparepart_3 = Service_sparepart.objects.create(
            quantity=5,
            service_id=cls.service_2,
            sparepart_id=cls.sparepart_2
        )

        # Setting up time data for test comparison
        cls.created_at_1 = cls.service_1.created_at + timedelta(hours=7)
        cls.created_at_2 = cls.service_2.created_at + timedelta(hours=7)

        return super().setUpTestData()

    def test_admin_successfully_access_service_list(self) -> None:
        """
        Ensure admin can get service list successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.service_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'], [
            {
                'service_id': self.service_1.service_id,
                'created_at': self.created_at_1.strftime('%d-%m-%Y %H:%M:%S'),
                'police_number': self.service_1.police_number,
                'mechanic': self.service_1.mechanic_id.name,
                'customer': self.service_1.customer_id.name,
                'customer_contact': self.service_1.customer_id.contact,
                'total_price_of_service': 910000,
                'is_paid_off': self.service_1.is_paid_off,
                'deposit': str(self.service_1.deposit),
                'discount': str(self.service_1.discount),
                'service_actions': [
                    {
                        'service_action_id': self.action_1.service_action_id,
                        'service_name': self.action_1.name,
                        'cost': str(self.action_1.cost)
                    },
                    {
                        'service_action_id': self.action_2.service_action_id,
                        'service_name': self.action_2.name,
                        'cost': str(self.action_2.cost)
                    },
                    {
                        'service_action_id': self.action_3.service_action_id,
                        'service_name': self.action_3.name,
                        'cost': str(self.action_3.cost)
                    }
                ],
                'service_spareparts': [
                    {
                        'service_sparepart_id': self.service_sparepart_1.service_sparepart_id,
                        'sparepart': self.service_sparepart_1.sparepart_id.name,
                        'quantity': self.service_sparepart_1.quantity,
                        'total_price':
                        int(self.service_sparepart_1.sparepart_id.install_price * self.service_sparepart_1.quantity)
                    }
                ]
            },
            {
                'service_id': self.service_2.service_id,
                'created_at': self.created_at_2.strftime('%d-%m-%Y %H:%M:%S'),
                'police_number': self.service_2.police_number,
                'mechanic': self.service_2.mechanic_id.name,
                'customer': self.service_2.customer_id.name,
                'customer_contact': self.service_2.customer_id.contact,
                'total_price_of_service': 725000,
                'is_paid_off': self.service_2.is_paid_off,
                'deposit': str(self.service_2.deposit),
                'discount': str(self.service_2.discount),
                'service_actions': [],
                'service_spareparts': [
                    {
                        'service_sparepart_id': self.service_sparepart_2.service_sparepart_id,
                        'sparepart': self.service_sparepart_2.sparepart_id.name,
                        'quantity': self.service_sparepart_2.quantity,
                        'total_price':
                        int(self.service_sparepart_2.sparepart_id.install_price * self.service_sparepart_2.quantity)
                    },
                    {
                        'service_sparepart_id': self.service_sparepart_3.service_sparepart_id,
                        'sparepart': self.service_sparepart_3.sparepart_id.name,
                        'quantity': self.service_sparepart_3.quantity,
                        'total_price':
                        int(self.service_sparepart_3.sparepart_id.install_price * self.service_sparepart_3.quantity)
                    }
                ]
            }
        ])

    def test_nonlogin_user_failed_to_access_service_list(self) -> None:
        """
        Ensure non-login user cannot access service list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.service_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_service_list(self) -> None:
        """
        Ensure non-admin user cannot access service list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.service_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class ServiceAddTestCase(SetTestCase):
    service_add_url = reverse('service_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up mechanic data
        cls.mechanic = Mechanic.objects.create(
            name='Bodger Bloger',
            contact='086206164404',
            address='Honeywood'
        )

        # Setting up customer data
        cls.customer = Customer.objects.create(
            name='Bartholomew Osiris Bladesong',
            contact='082541684051',
        )

        # Setting up storage data
        cls.storage = Storage.objects.create(code='MN-9')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Lavish Chateau')

        # Setting up category data
        cls.category = Category.objects.create(name='Food')

        # Setting up sparepart data
        cls.sparepart = Sparepart.objects.create(
            name='Chorcoal Cupcake',
            partnumber='JFLJ23-Aj',
            quantity=50,
            motor_type='Human',
            sparepart_type='Spices',
            price=105000,
            workshop_price=100000,
            install_price=110000,
            brand_id=cls.brand,
            category_id=cls.category,
            storage_id=cls.storage
        )

        cls.data = {
            'mechanic_id': cls.mechanic.mechanic_id,
            'customer_id': cls.customer.customer_id,
            'police_number': 'B 8546 D',
            'motor_type': 'Yamaha',
            'is_paid_off': False,
            'deposit': 30000,
            'discount': 5000,
            'service_actions': [
                {
                    'service_name': 'Angkat Spion',
                    'cost': 50000,
                },
                {
                    'service_name': 'Isi Bensin',
                    'cost': 10000,
                }
            ],
            'service_spareparts': [
                {
                    'sparepart_id': cls.sparepart.sparepart_id,
                    'quantity': 2
                }
            ]
        }

        cls.incomplete_data = {
            'mechanic_id': cls.mechanic.mechanic_id,
            'customer_id': cls.customer.customer_id,
            'police_number': 'B 8546 D',
            'motor_type': 'Yamaha',
            'is_paid_off': False
        }

        return super().setUpTestData()

    def test_admin_successfully_add_service(self) -> None:
        """
        Ensure admin can add new service data with it's content
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.service_add_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Data servis berhasil ditambah')
        self.assertEqual(response.data['mechanic_id'], self.mechanic.mechanic_id)
        self.assertEqual(response.data['customer_id'], self.customer.customer_id)
        self.assertEqual(response.data['police_number'], self.data['police_number'])
        self.assertEqual(response.data['motor_type'], self.data['motor_type'])
        self.assertEqual(response.data['is_paid_off'], self.data['is_paid_off'])
        self.assertEqual(int(response.data['deposit']), self.data['deposit'])
        self.assertEqual(int(response.data['discount']), self.data['discount'])

        self.assertEqual(response.data['service_actions'][0]['service_name'],
                         self.data['service_actions'][0]['service_name'])

        self.assertEqual(int(response.data['service_actions'][0]['cost']),
                         self.data['service_actions'][0]['cost'])

        self.assertEqual(response.data['service_actions'][1]['service_name'],
                         self.data['service_actions'][1]['service_name'])

        self.assertEqual(int(response.data['service_actions'][1]['cost']),
                         self.data['service_actions'][1]['cost'])

        self.assertEqual(response.data['service_spareparts'][0]['sparepart_id'],
                         self.data['service_spareparts'][0]['sparepart_id'])

        self.assertEqual(response.data['service_spareparts'][0]['quantity'],
                         self.data['service_spareparts'][0]['quantity'])

        # ensure sparepart quantity will be subtracted by service_sparepart's quantity
        # after service successfully added
        self.assertEqual(Sparepart.objects.all()[0].quantity, 48)

    def test_nonlogin_user_failed_to_add_service(self) -> None:
        """
        Ensure non-login cannot add new service data with it's content
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.service_add_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_failed_to_add_service(self) -> None:
        """
        Ensure non-admin cannot add new service data with it's content
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.service_add_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_add_service_with_empty_data(self) -> None:
        """
        Ensure admin cannot add service with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.service_add_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data servis tidak sesuai / tidak lengkap')

    def test_admin_failed_to_add_service_with_incomplete_data(self) -> None:
        """
        Ensure admin cannot add data service with incomplete data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.service_add_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data servis tidak sesuai / tidak lengkap')


class ServiceUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up mechanic data
        cls.mechanic = Mechanic.objects.create(
            name='Bodger Bloger',
            contact='086206164404',
            address='Honeywood'
        )

        # Setting up customer data
        cls.customer = Customer.objects.create(
            name='Bartholomew Osiris Bladesong',
            contact='082541684051',
        )

        # Setting up storage data
        cls.storage = Storage.objects.create(code='MN-9')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Lavish Chateau')

        # Setting up category data
        cls.category = Category.objects.create(name='Food')

        # Setting up sparepart data
        cls.sparepart = Sparepart.objects.create(
            name='Chorcoal Cupcake',
            partnumber='JFLJ23-Aj',
            quantity=50,
            motor_type='Human',
            sparepart_type='Spices',
            price=105000,
            workshop_price=100000,
            install_price=110000,
            brand_id=cls.brand,
            category_id=cls.category,
            storage_id=cls.storage
        )
        cls.sparepart_2 = Sparepart.objects.create(
            name='Chorcoal Cupcake 2',
            partnumber='JFLJ23-Aj',
            quantity=100,
            motor_type='Human',
            sparepart_type='Spices',
            price=105000,
            workshop_price=100000,
            install_price=110000,
            brand_id=cls.brand,
            category_id=cls.category,
            storage_id=cls.storage
        )

        return super().setUpTestData()

    def setUp(self) -> None:
        self.service = Service.objects.create(
            police_number='B 1293 A',
            motor_type='Beneli',
            deposit=500000,
            discount=20000,
            user_id=self.user,
            mechanic_id=self.mechanic,
            customer_id=self.customer
        )

        # Getting newly added service it's service_id then set it to kwargs in reverse url
        self.service_update_url = reverse('service_update', kwargs={'service_id': self.service.service_id})

        # Setting up service actions
        self.action_1 = Service_action.objects.create(
            name='Pompa Ban',
            cost='10000',
            service_id=self.service
        )
        self.action_2 = Service_action.objects.create(
            name='Bongkar Mesin',
            cost='800000',
            service_id=self.service
        )

        # Setting up service sparepart
        self.service_sparepart = Service_sparepart.objects.create(
            quantity=5,
            service_id=self.service,
            sparepart_id=self.sparepart
        )
        self.service_sparepart_2 = Service_sparepart.objects.create(
            quantity=13,
            service_id=self.service,
            sparepart_id=self.sparepart_2
        )

        self.data = {
            'mechanic_id': self.mechanic.mechanic_id,
            'customer_id': self.customer.customer_id,
            'police_number': 'B 8546 D',
            'motor_type': 'Yamaha',
            'is_paid_off': False,
            'deposit': 600000,
            'discount': 5000,
            'service_actions': [
                {
                    'service_action_id': self.action_1.service_action_id,
                    'service_name': 'Pompa Ban',
                    'cost': 10000,
                },
                {
                    'service_action_id': self.action_2.service_action_id,
                    'service_name': 'Bongkar Mesin',
                    'cost': 800000,
                }
            ],
            'service_spareparts': [
                {
                    'service_sparepart_id': self.service_sparepart.service_sparepart_id,
                    'sparepart_id': self.sparepart.sparepart_id,
                    'quantity': 3
                },
                {
                    'service_sparepart_id': self.service_sparepart_2.service_sparepart_id,
                    'sparepart_id': self.sparepart_2.sparepart_id,
                    'quantity': 10
                }
            ]
        }

        self.incomplete_data = {
            'motor_type': 'Yamaha',
            'is_paid_off': False,
            'deposit': 600000,
            'discount': 5000,
            'service_actions': [
                {
                    'service_action_id': self.action_1.service_action_id,
                    'service_name': 'Pompa Ban',
                    'cost': 10000,
                },
            ],
            'service_spareparts': [
                {
                    'service_sparepart_id': self.service_sparepart.service_sparepart_id,
                    'sparepart_id': self.sparepart.sparepart_id,
                    'quantity': 3
                }
            ]
        }

        return super().setUp()

    def test_admin_successfully_update_service(self) -> None:
        """
        Ensure admin can update service data successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.service_update_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Data servis berhasil dirubah')
        self.assertEqual(response.data['mechanic_id'], self.data['mechanic_id'])
        self.assertEqual(response.data['customer_id'], self.data['customer_id'])
        self.assertEqual(response.data['police_number'], self.data['police_number'])
        self.assertEqual(response.data['motor_type'], self.data['motor_type'])
        self.assertEqual(response.data['is_paid_off'], self.data['is_paid_off'])
        self.assertEqual(int(response.data['deposit']), self.data['deposit'])
        self.assertEqual(int(response.data['discount']), self.data['discount'])

        self.assertEqual(response.data['service_actions'][0]['service_action_id'],
                         self.data['service_actions'][0]['service_action_id'])

        self.assertEqual(response.data['service_actions'][0]['service_name'],
                         self.data['service_actions'][0]['service_name'])

        self.assertEqual(int(response.data['service_actions'][0]['cost']),
                         self.data['service_actions'][0]['cost'])

        self.assertEqual(response.data['service_actions'][1]['service_action_id'],
                         self.data['service_actions'][1]['service_action_id'])

        self.assertEqual(response.data['service_actions'][1]['service_name'],
                         self.data['service_actions'][1]['service_name'])

        self.assertEqual(int(response.data['service_actions'][1]['cost']),
                         self.data['service_actions'][1]['cost'])

        self.assertEqual(response.data['service_spareparts'][0]['service_sparepart_id'],
                         self.data['service_spareparts'][0]['service_sparepart_id'])

        self.assertEqual(response.data['service_spareparts'][0]['sparepart_id'],
                         self.data['service_spareparts'][0]['sparepart_id'])

        self.assertEqual(response.data['service_spareparts'][0]['quantity'],
                         self.data['service_spareparts'][0]['quantity'])

        # ensure sparepart quantity will be subtracted by service_sparepart's quantity
        # after service successfully updated
        self.assertEqual(Sparepart.objects.all().order_by('sparepart_id')[0].quantity, 52)
        self.assertEqual(Sparepart.objects.all().order_by('sparepart_id')[1].quantity, 103)

    def test_nonlogin_failed_to_update_service(self) -> None:
        """
        Ensure non-login user cannot update service
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.service_update_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_update_service(self) -> None:
        """
        Ensure non-admin user cannot update service
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.service_update_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_update_nonexist_service(self) -> None:
        """
        Ensure admin cannot / Failed update non-exist service
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('service_update', kwargs={'service_id': 89152}),
                                   self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data servis tidak ditemukan')

    def test_admin_failed_to_update_service_with_empty_data(self) -> None:
        """
        Ensure admin cannot update service with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.service_update_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data servis tidak sesuai / tidak lengkap')

    def test_admin_failed_to_update_service_with_incomplete_data(self) -> None:
        """
        Ensure admin cannot update service with incomplete data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.service_update_url, self.incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data servis tidak sesuai / tidak lengkap')


class ServiceDeleteTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up mechanic data
        cls.mechanic = Mechanic.objects.create(
            name='Bodger Bloger',
            contact='086206164404',
            address='Honeywood'
        )

        # Setting up customer data
        cls.customer = Customer.objects.create(
            name='Bartholomew Osiris Bladesong',
            contact='082541684051',
        )

        # Setting up sparepart data
        cls.sparepart = Sparepart.objects.create(
            name='Check Point Scroll',
            partnumber='JFLJ23-Aj',
            quantity=50,
            motor_type='Mage',
            sparepart_type='Magical Scroll',
            price=105000,
            workshop_price=100000,
            install_price=110000,
        )

        return super().setUpTestData()

    def setUp(self) -> None:
        self.service = Service.objects.create(
            police_number='B 1293 A',
            motor_type='Beneli',
            deposit=500000,
            discount=20000,
            user_id=self.user,
            mechanic_id=self.mechanic,
            customer_id=self.customer
        )

        # Getting newly added service it's service_id then set it to kwargs in reverse url
        self.service_delete_url = reverse('service_delete', kwargs={'service_id': self.service.service_id})

        # Setting up service actions
        Service_action.objects.create(
            name='Pompa Ban',
            cost='10000',
            service_id=self.service
        )

        # Setting up service sparepart
        Service_sparepart.objects.create(
            quantity=13,
            service_id=self.service,
            sparepart_id=self.sparepart
        )

        return super().setUp()

    def test_admin_successfully_delete_service(self) -> None:
        """
        Ensure admin can delete service data successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.service_delete_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data servis berhasil dihapus')
        self.assertEqual(len(Service.objects.all()), 0)
        self.assertEqual(len(Service_action.objects.all()), 0)
        self.assertEqual(len(Service_sparepart.objects.all()), 0)

        # ensure sparepart quantity will be added (+) by service_sparepart's quantity
        # after service successfully deleted
        self.assertEqual(Sparepart.objects.all().order_by('sparepart_id')[0].quantity, 63)

    def test_nonlogin_user_failed_to_delete_service(self) -> None:
        """
        Ensure non-login user cannot delete service
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.service_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_delete_service(self) -> None:
        """
        Ensure non-admin user cannot delete service
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.service_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_delete_nonexist_service(self) -> None:
        """
        Ensure admin cannot / failed to delete non-exist service
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('service_delete', kwargs={'service_id': 85635}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data servis tidak ditemukan')


class StorageListTestCase(SetTestCase):
    storage_url = reverse('storage_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # setting up storage data
        cls.storage = Storage.objects.create(
            code='A-23',
            location='1',
            is_full=True
        )
        Storage.objects.create(
            code='OT-3',
            location='2',
            is_full=False
        )

        return super().setUpTestData()

    def test_admin_successfully_access_storage_list(self) -> None:
        """
        Ensure admin can get storage list successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.storage_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'][0]['code'], self.storage.code)
        self.assertEqual(response.data['results'][0]['location'], self.storage.location)
        self.assertEqual(response.data['results'][0]['is_full'], self.storage.is_full)

    def test_nonlogin_user_failed_to_access_storage_list(self) -> None:
        """
        Ensure non-login user cannot access storage list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.storage_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_storage_list(self) -> None:
        """
        Ensure non-admin user cannot access storage list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.storage_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class StorageAddTestCase(SetTestCase):
    storage_add_url = reverse('storage_add')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.data = {
            'code': 'A-23',
            'location': '1',
            'is_full': True
        }
        cls.incomplete_data = {
            'location': '1',
            'is_full': True
        }

        return super().setUpTestData()

    def test_admin_successfully_add_storage(self) -> None:
        """
        Ensure admin can add new storage successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.storage_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Data lokasi penyimpanan berhasil ditambah')
        self.assertEqual(response.data['code'], self.data['code'])
        self.assertEqual(response.data['location'], self.data['location'])
        self.assertEqual(response.data['is_full'], self.data['is_full'])

    def test_nonlogin_user_failed_to_add_new_storage(self) -> None:
        """
        Ensure non-login user cannot add new storage
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.storage_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_add_new_storage(self) -> None:
        """
        Ensure non-admin user cannot add new storage
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.storage_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_add_storage_with_empty_data(self) -> None:
        """
        Ensure admin cannot add storage with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.storage_add_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data lokasi penyimpanan tidak sesuai / tidak lengkap')

    def test_admin_failed_to_add_storage_with_incomplete_data(self) -> None:
        """
        Ensure admin cannot add storage with incomplete data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.storage_add_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data lokasi penyimpanan tidak sesuai / tidak lengkap')


class StorageUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up storage data
        cls.storage = Storage.objects.create(
            code='DB-14',
            location='2',
            is_full=True
        )

        cls.storage_update_url = reverse(
            'storage_update',
            kwargs={'storage_id': cls.storage.storage_id}
        )

        # Setting up input data
        cls.data = {
            'code': 'DB-14',
            'location': '2',
            'is_full': False
        }
        # Setting up input data
        cls.incomplete_data = {
            'is_full': False
        }

        return super().setUpTestData()

    def test_successfully_update_storage(self) -> None:
        """
        Ensure admin can update storage successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.storage_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Data lokasi penyimpanan berhasil dirubah')
        self.assertEqual(response.data['code'], self.data['code'])
        self.assertEqual(response.data['location'], self.data['location'])
        self.assertEqual(response.data['is_full'], self.data['is_full'])

    def test_nonlogin_user_failed_to_update_storage(self) -> None:
        """
        Ensure non-login user cannot update storage
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.storage_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_update_storage(self) -> None:
        """
        Ensure non-admin user cannot update storage
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.storage_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_update_nonexist_storage(self) -> None:
        """
        Ensure admin cannot update non-exist storage
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('storage_update', kwargs={'storage_id': 526523}),
                                   self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data lokasi penyimpanan tidak ditemukan')

    def test_admin_failed_to_update_storage_with_empty_data(self) -> None:
        """
        Ensure admin cannot update data storage with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.storage_update_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data lokasi penyimpanan tidak sesuai / tidak lengkap')

    def test_admin_failed_to_update_storage_with_incomplete_data(self) -> None:
        """
        Ensure admin cannot update data storage with incomplete data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.storage_update_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data lokasi penyimpanan tidak sesuai / tidak lengkap')


class StorageDeleteTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Storage.objects.create(
            code='KF-13',
            location='1',
            is_full=False
        )

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up storage data
        self.storage = Storage.objects.create(
            code='DB-14',
            location='2',
            is_full=True
        )

        self.storage_delete_url = reverse(
            'storage_delete',
            kwargs={'storage_id': self.storage.storage_id}
        )

        return super().setUp()

    def test_admin_successfully_delete_storage(self) -> None:
        """
        Ensure admin can delete storage successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.storage_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data lokasi penyimpanan berhasil dihapus')
        self.assertEqual(len(Storage.objects.all()), 1)

    def test_nonlogin_user_failed_to_delete_storage(self) -> None:
        """
        Ensure non-login user cannot delete storage
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.storage_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_delete_storage(self) -> None:
        """
        Ensure non-admin user cannot delete storage
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.storage_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_delete_nonexist_storage(self) -> None:
        """
        Ensure admin cannot to delete non-exist storage
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('storage_delete', kwargs={'storage_id': 86591}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data lokasi penyimpanan tidak ditemukan')


class BrandListTestCase(SetTestCase):
    brand_url = reverse('brand_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up brand data
        cls.brand = Brand.objects.create(name='The Way Of King')
        Brand.objects.create(name='Elantris')

        return super().setUpTestData()

    def test_admin_successfully_access_brand_list(self) -> None:
        """
        Ensure admin can get brand list successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.brand_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'][0]['name'], 'The Way Of King')
        self.assertEqual(response.data['results'][1]['name'], 'Elantris')

    def test_nonlogin_user_failed_to_access_brand_list(self) -> None:
        """
        Ensure non-login user cannot access brand list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.brand_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_brand_list(self) -> None:
        """
        Ensure non-admin user cannot access brand list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.brand_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_successfully_searching_brand_with_result(self) -> None:
        """
        Ensure admin who searching brand with correct keyword get correct result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('brand_list') + f'?q={self.brand.name}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['results'], [
            {
                'brand_id': self.brand.brand_id,
                'name': 'The Way Of King',
            }
        ])

    def test_admin_successfully_searching_brand_without_result(self) -> None:
        """
        Ensure admin search brand that doesn't exist get empty result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('brand_list') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 0)
        self.assertEqual(response.data['message'], 'Brand / Merek sparepart yang dicari tidak ditemukan')


class BrandAddTestCase(SetTestCase):
    brand_add_url = reverse('brand_add')

    def test_admin_successfully_add_brand(self) -> None:
        """
        Ensure admin can add new brand successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.brand_add_url, {'name': 'Beauregard'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Data merek / brand berhasil ditambah')
        self.assertEqual(response.data['name'], 'Beauregard')

    def test_nonlogin_user_failed_to_add_new_brand(self) -> None:
        """
        Ensure non-login user cannot add new brand
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.brand_add_url, {'name': 'Beauregard'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_add_new_brand(self) -> None:
        """
        Ensure non-admin user cannot add new brand
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.brand_add_url, {'name': 'Beauregard'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_add_brand_with_empty_data(self) -> None:
        """
        Ensure admin cannot add brand with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.brand_add_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data merek / brand tidak sesuai / tidak lengkap')


class BrandUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up brand data
        cls.brand = Brand.objects.create(name='Fresh Cut Grass')

        cls.brand_update_url = reverse('brand_update', kwargs={'brand_id': cls.brand.brand_id})

        return super().setUpTestData()

    def test_successfully_update_brand(self) -> None:
        """
        Ensure admin can update brand successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.brand_update_url, {'name': 'FCG'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Data merek / brand berhasil dirubah')
        self.assertEqual(response.data['name'], 'FCG')

    def test_nonlogin_user_failed_to_update_brand(self) -> None:
        """
        Ensure non-login user cannot update brand
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.brand_update_url, {'name': 'FCG'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_update_brand(self) -> None:
        """
        Ensure non-admin user cannot update brand
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.brand_update_url, {'name': 'FCG'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_update_nonexist_brand(self) -> None:
        """
        Ensure admin cannot update non-exist brand
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('brand_update', kwargs={'brand_id': 526523}),
                                   {'name': 'FCG'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data merek / brand tidak ditemukan')

    def test_admin_failed_to_update_brand_with_empty_data(self) -> None:
        """
        Ensure admin cannot update data brand with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.brand_update_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data merek / brand tidak sesuai / tidak lengkap')


class BrandDeleteTestCase(SetTestCase):
    def setUp(self) -> None:
        # Setting up brand data
        self.brand = Brand.objects.create(name='Malazan')

        self.brand_delete_url = reverse('brand_delete', kwargs={'brand_id': self.brand.brand_id})

        return super().setUp()

    def test_admin_successfully_delete_brand(self) -> None:
        """
        Ensure admin can delete brand successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.brand_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data merek / brand berhasil dihapus')
        self.assertEqual(len(Brand.objects.all()), 0)

    def test_nonlogin_user_failed_to_delete_brand(self) -> None:
        """
        Ensure non-login user cannot delete brand
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.brand_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_delete_brand(self) -> None:
        """
        Ensure non-admin user cannot delete brand
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.brand_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_delete_nonexist_brand(self) -> None:
        """
        Ensure admin cannot to delete non-exist brand
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('brand_delete', kwargs={'brand_id': 86591}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data merek / brand tidak ditemukan')


class CategoryListTestCase(SetTestCase):
    category_url = reverse('category_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up category data
        cls.category = Category.objects.create(name='Oil')
        Category.objects.create(name='Bodypart')

        return super().setUpTestData()

    def test_admin_successfully_access_category_list(self) -> None:
        """
        Ensure admin can get category list successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'][0]['name'], 'Oil')
        self.assertEqual(response.data['results'][1]['name'], 'Bodypart')

    def test_nonlogin_user_failed_to_access_category_list(self) -> None:
        """
        Ensure non-login user cannot access category list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_category_list(self) -> None:
        """
        Ensure non-admin user cannot access category list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_successfully_searching_category_with_result(self) -> None:
        """
        Ensure admin who searching category with correct keyword get correct result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('category_list') + f'?q={self.category.name}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['results'], [
            {
                'category_id': self.category.category_id,
                'name': 'Oil',
            }
        ])

    def test_admin_successfully_searching_category_without_result(self) -> None:
        """
        Ensure admin search category that doesn't exist get empty result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('category_list') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 0)
        self.assertEqual(response.data['message'], 'Kategori sparepart yang dicari tidak ditemukan')


class CategoryAddTestCase(SetTestCase):
    category_add_url = reverse('category_add')

    def test_admin_successfully_add_category(self) -> None:
        """
        Ensure admin can add new category successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.category_add_url, {'name': 'Lamp'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Data kategori berhasil ditambah')
        self.assertEqual(len(Category.objects.all()), 1)
        self.assertEqual(response.data['name'], 'Lamp')

    def test_nonlogin_user_failed_to_add_new_category(self) -> None:
        """
        Ensure non-login user cannot add new category
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.category_add_url, {'name': 'Lamp'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_add_new_category(self) -> None:
        """
        Ensure non-admin user cannot add new category
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.category_add_url, {'name': 'Lamp'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_add_category_with_empty_data(self) -> None:
        """
        Ensure admin cannot add category with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.category_add_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data kategori tidak sesuai / tidak lengkap')


class CategoryUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up category data
        cls.category = Category.objects.create(name='Dawnguards')

        cls.category_update_url = reverse('category_update', kwargs={'category_id': cls.category.category_id})

        return super().setUpTestData()

    def test_successfully_update_category(self) -> None:
        """
        Ensure admin can update category successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.category_update_url, {'name': 'Mistborn'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Data kategori berhasil dirubah')
        self.assertEqual(response.data['name'], 'Mistborn')

    def test_nonlogin_user_failed_to_update_category(self) -> None:
        """
        Ensure non-login user cannot update category
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.category_update_url, {'name': 'Mistborn'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_update_category(self) -> None:
        """
        Ensure non-admin user cannot update category
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.category_update_url, {'name': 'Mistborn'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_update_nonexist_category(self) -> None:
        """
        Ensure admin cannot update non-exist category
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('category_update', kwargs={'category_id': 526523}),
                                   {'name': 'Mistborn'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data kategori tidak ditemukan')

    def test_admin_failed_to_update_category_with_empty_data(self) -> None:
        """
        Ensure admin cannot update data category with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.category_update_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data kategori tidak sesuai / tidak lengkap')


class CategoryDeleteTestCase(SetTestCase):
    def setUp(self) -> None:
        # Setting up category data
        self.category = Category.objects.create(name='Malazan')

        self.category_delete_url = reverse('category_delete', kwargs={'category_id': self.category.category_id})

        return super().setUp()

    def test_admin_successfully_delete_category(self) -> None:
        """
        Ensure admin can delete category successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.category_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data kategori berhasil dihapus')
        self.assertEqual(len(Brand.objects.all()), 0)

    def test_nonlogin_user_failed_to_delete_category(self) -> None:
        """
        Ensure non-login user cannot delete category
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.category_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_delete_category(self) -> None:
        """
        Ensure non-admin user cannot delete category
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.category_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_delete_nonexist_category(self) -> None:
        """
        Ensure admin cannot to delete non-exist category
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('category_delete', kwargs={'category_id': 86591}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data kategori tidak ditemukan')


class CustomerListTestCase(SetTestCase):
    customer_url = reverse('customer_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # setting customer data
        cls.customer = Customer.objects.create(
            name='Preston Garvey',
            contact='085701530830',
        )
        cls.customer_2 = Customer.objects.create(
            name='Robert MacCready',
            contact='085163511040',
        )

        # Setting up sparepart data
        cls.sparepart = Sparepart.objects.create(
            name='Grimoire',
            partnumber='HGHA-189751',
            quantity=150,
            limit=50,
            motor_type='Yamaha',
            sparepart_type='Book',
            price=155000,
            workshop_price=150000,
            install_price=165000
        )

        # Setting up service data for customer
        cls.service = Service.objects.create(
            police_number='B 1238 AS',
            motor_type='Kymco C100',
            discount=10000,
            customer_id=cls.customer
        )
        Service_action.objects.create(
            name='Angkat Kaki',
            cost=150000,
            service_id=cls.service
        )
        Service_sparepart.objects.create(
            service_id=cls.service,
            sparepart_id=cls.sparepart,
            quantity=5,
        )

        cls.service_2 = Service.objects.create(
            police_number='B 1236 DS',
            motor_type='Kymco C100',
            discount=2000,
            customer_id=cls.customer_2
        )
        Service_action.objects.create(
            name='Angkat Tangan',
            cost=30000,
            service_id=cls.service_2
        )

        return super().setUpTestData()

    def test_admin_successfully_access_customer_list(self) -> None:
        """
        Ensure admin can get customer list successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'][0]['name'], self.customer.name)
        self.assertEqual(response.data['results'][0]['contact'], self.customer.contact)
        self.assertEqual(response.data['results'][0]['number_of_service'], 1)
        self.assertEqual(response.data['results'][0]['total_payment'], 965000)
        self.assertEqual(response.data['results'][1]['name'], self.customer_2.name)
        self.assertEqual(response.data['results'][1]['contact'], self.customer_2.contact)
        self.assertEqual(response.data['results'][1]['number_of_service'], 1)
        self.assertEqual(response.data['results'][1]['total_payment'], 28000)

    def test_nonlogin_user_failed_to_access_customer_list(self) -> None:
        """
        Ensure non-login user cannot access customer list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_customer_list(self) -> None:
        """
        Ensure non-admin user cannot access customer list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_successfully_searching_customer_with_result(self) -> None:
        """
        Ensure admin who searching customer with correct keyword get correct result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('customer_list') + f'?q={self.customer.name}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['results'], [
            {
                'customer_id': self.customer.customer_id,
                'name': self.customer.name,
                'contact': self.customer.contact,
                'number_of_service': 1,
                'total_payment': 965000
            }
        ])

    def test_admin_successfully_searching_customer_without_result(self) -> None:
        """
        Ensure admin search customer that doesn't exist get empty result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('customer_list') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 0)
        self.assertEqual(response.data['message'], 'Pelanggan yang dicari tidak ditemukan')


class CustomerAddTestCase(SetTestCase):
    customer_add_url = reverse('customer_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up input data
        cls.data = {
            'name': 'Piper Wright',
            'contact':  '085701530830',
        }
        cls.incomplete_data = {
            'contact':  '085687028044',
        }

        return super().setUpTestData()

    def test_admin_successfully_add_customer(self) -> None:
        """
        Ensure admin can add new customer successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.customer_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Data pelanggan berhasil ditambah')
        self.assertEqual(response.data['name'], self.data['name'])
        self.assertEqual(response.data['contact'], self.data['contact'])

    def test_nonlogin_user_failed_to_add_new_customer(self) -> None:
        """
        Ensure non-login user cannot add new customer
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.customer_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_add_new_customer(self) -> None:
        """
        Ensure non-admin user cannot add new customer
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.customer_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_add_customer_with_empty_data(self) -> None:
        """
        Ensure admin cannot add customer with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.customer_add_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data pelanggan tidak sesuai / tidak lengkap')

    def test_admin_failed_to_add_customer_with_incomplete_data(self) -> None:
        """
        Ensure admin cannot add customer with incomplete data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.customer_add_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data pelanggan tidak sesuai / tidak lengkap')


class CustomerUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting customer data
        cls.customer = Customer.objects.create(
           name='The Father',
           contact='083515301351',
        )

        # Getting customer update url with customer_id
        cls.customer_update_url = reverse(
            'customer_update',
            kwargs={'customer_id': cls.customer.customer_id}
        )

        # Setting up input data
        cls.data = {
            'name': 'Shaun',
            'contact':  '085701530830',
        }
        cls.incomplete_data = {
            'contact':  '085687028044',
        }

        return super().setUpTestData()

    def test_successfully_update_customer(self) -> None:
        """
        Ensure admin can update customer successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.customer_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Data pelanggan berhasil dirubah')
        self.assertEqual(response.data['name'], self.data['name'])
        self.assertEqual(response.data['contact'], self.data['contact'])

    def test_nonlogin_user_failed_to_update_customer(self) -> None:
        """
        Ensure non-login user cannot update customer
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.customer_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_update_customer(self) -> None:
        """
        Ensure non-admin user cannot update customer
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.customer_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_update_nonexist_customer(self) -> None:
        """
        Ensure admin cannot update non-exist customer
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('customer_update', kwargs={'customer_id': 526523}),
                                   self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data pelanggan tidak ditemukan')

    def test_admin_failed_to_update_customer_with_empty_data(self) -> None:
        """
        Ensure admin cannot update data customer with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.customer_update_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data pelanggan tidak sesuai / tidak lengkap')

    def test_admin_failed_to_update_customer_with_incomplete_data(self) -> None:
        """
        Ensure admin cannot update data customer with incomplete data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.customer_update_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data pelanggan tidak sesuai / tidak lengkap')


class CustomerDeleteTestCase(SetTestCase):
    def setUp(self) -> None:
        # Setting up storage data
        self.customer = Customer.objects.create(
            name='The Father',
            contact='083515301351'
        )
        Customer.objects.create(
            name='The Minuteman',
            contact='68486048601'
        )

        self.customer_delete_url = reverse(
            'customer_delete',
            kwargs={'customer_id': self.customer.customer_id}
        )

        return super().setUp()

    def test_admin_successfully_delete_customer(self) -> None:
        """
        Ensure admin can delete customer successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.customer_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data pelanggan berhasil dihapus')
        self.assertEqual(Customer.objects.count(), 1)

    def test_nonlogin_user_failed_to_delete_customer(self) -> None:
        """
        Ensure non-login user cannot delete customer
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.customer_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_delete_customer(self) -> None:
        """
        Ensure non-admin user cannot delete customer
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.customer_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_delete_nonexist_customer(self) -> None:
        """
        Ensure admin cannot to delete non-exist customer
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('customer_delete', kwargs={'customer_id': 86591}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data pelanggan tidak ditemukan')


class SalesmanListTestCase(SetTestCase):
    salesman_url = reverse('salesman_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up supplier data
        cls.supplier = Supplier.objects.create(
            name='Institute',
            contact='085340153504',
            rekening_number='8468464056156',
            rekening_name='Father',
            rekening_bank='Bank Commonwealth'
        )

        # setting up salesman data
        cls.salesman = Salesman.objects.create(
            name='The Courier',
            contact='084052631053',
            responsibility='Package',
            supplier_id=cls.supplier
        )
        Salesman.objects.create(
            name='The Lone Wanderer',
            contact='082351351010',
            responsibility='Vault',
            supplier_id=cls.supplier
        )

        return super().setUpTestData()

    def test_admin_successfully_access_salesman_list(self) -> None:
        """
        Ensure admin can get salesman list successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.salesman_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'][0]['name'], self.salesman.name)
        self.assertEqual(response.data['results'][0]['contact'], self.salesman.contact)
        self.assertEqual(response.data['results'][0]['supplier'], self.salesman.supplier_id.name)
        self.assertEqual(response.data['results'][0]['responsibility'], self.salesman.responsibility)

    def test_nonlogin_user_failed_to_access_salesman_list(self) -> None:
        """
        Ensure non-login user cannot access salesman list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.salesman_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_access_salesman_list(self) -> None:
        """
        Ensure non-admin user cannot access salesman list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.salesman_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_successfully_searching_salesman_with_result(self) -> None:
        """
        Ensure admin who searching salesman with correct keyword get correct result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('salesman_list') + f'?q={self.salesman.name}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['results'], [
            {
                'salesman_id': self.salesman.salesman_id,
                'name': self.salesman.name,
                'contact': self.salesman.contact,
                'supplier': self.salesman.supplier_id.name,
                'responsibility': self.salesman.responsibility
            }
        ])

    def test_admin_successfully_searching_salesman_without_result(self) -> None:
        """
        Ensure admin search salesman that doesn't exist get empty result
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('salesman_list') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 0)
        self.assertEqual(response.data['message'], 'Salesman yang dicari tidak ditemukan')


class SalesmanAddTestCase(SetTestCase):
    salesman_add_url = reverse('salesman_add')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.supplier = Supplier.objects.create(
            name='Institute',
            contact='085340153504',
            rekening_number='8468464056156',
            rekening_name='Father',
            rekening_bank='Bank Commonwealth'
        )

        # Setting up input data
        cls.data = {
            'name': 'Allura Vasoren',
            'contact': '085132135051',
            'supplier_id': cls.supplier.supplier_id,
            'responsibility': 'Magical Threat'
        }
        cls.incomplete_data = {
            'address': 'Allura Vysoren'
        }

        return super().setUpTestData()

    def test_admin_successfully_add_salesman(self) -> None:
        """
        Ensure admin can add new salesman successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.salesman_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Data salesman berhasil ditambah')
        self.assertEqual(response.data['name'], self.data['name'])
        self.assertEqual(response.data['contact'], self.data['contact'])
        self.assertEqual(response.data['supplier_id'], self.data['supplier_id'])
        self.assertEqual(response.data['responsibility'], self.data['responsibility'])

    def test_nonlogin_user_failed_to_add_new_salesman(self) -> None:
        """
        Ensure non-login user cannot add new salesman
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.salesman_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_add_new_salesman(self) -> None:
        """
        Ensure non-admin user cannot add new salesman
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.salesman_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_add_salesman_with_empty_data(self) -> None:
        """
        Ensure admin cannot add salesman with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.salesman_add_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data salesman tidak sesuai / tidak lengkap')

    def test_admin_failed_to_add_salesman_with_incomplete_data(self) -> None:
        """
        Ensure admin cannot add salesman with incomplete data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.salesman_add_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data salesman tidak sesuai / tidak lengkap')


class SalesmanUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting supplier data
        cls.supplier = Supplier.objects.create(
            name='Alpha Flight',
            contact='0850640564646',
            rekening_number='5466044654101',
            rekening_name='Logan',
            rekening_bank='Bank Of Canada'
        )

        # Setting salesman data
        cls.salesman = Salesman.objects.create(
            name='James Howlett',
            contact='083260466406',
            supplier_id=cls.supplier,
            responsibility="Mutant's Problems"
        )

        cls.salesman_update_url = reverse(
            'salesman_update',
            kwargs={'salesman_id': cls.salesman.salesman_id}
        )

        # Setting up input data
        cls.data = {
            'name': 'Logan',
            'contact': '085020260654',
            'supplier_id': cls.supplier.supplier_id,
            'responsibility': "Avenger's Problems"
        }
        cls.incomplete_data = {
            'name': 'Logan'
        }

        return super().setUpTestData()

    def test_successfully_update_salesman(self) -> None:
        """
        Ensure admin can update salesman successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.salesman_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Data salesman berhasil dirubah')
        self.assertEqual(response.data['name'], self.data['name'])
        self.assertEqual(response.data['contact'], self.data['contact'])
        self.assertEqual(response.data['supplier_id'], self.data['supplier_id'])
        self.assertEqual(response.data['responsibility'], self.data['responsibility'])

    def test_nonlogin_user_failed_to_update_salesman(self) -> None:
        """
        Ensure non-login user cannot update salesman
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.salesman_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_update_salesman(self) -> None:
        """
        Ensure non-admin user cannot update salesman
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.salesman_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_update_nonexist_salesman(self) -> None:
        """
        Ensure admin cannot update non-exist salesman
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('salesman_update', kwargs={'salesman_id': 526523}),
                                   self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data salesman tidak ditemukan')

    def test_admin_failed_to_update_salesman_with_empty_data(self) -> None:
        """
        Ensure admin cannot update data salesman with empty data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.salesman_update_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data salesman tidak sesuai / tidak lengkap')

    def test_admin_failed_to_update_salesman_with_incomplete_data(self) -> None:
        """
        Ensure admin cannot update data salesman with incomplete data / input
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.salesman_update_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data salesman tidak sesuai / tidak lengkap')


class SalesmanDeleteTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting supplier data
        cls.supplier = Supplier.objects.create(
            name='Paige',
            contact='083151051560',
            rekening_number='4466846011015',
            rekening_name='Clamentine',
            rekening_bank='Bank SalvaierWood'
        )

        return super().setUpTestData()

    def setUp(self) -> None:
        # Setting up storage data
        self.salesman = Salesman.objects.create(
            name='Clamentine',
            contact='086054056640',
            supplier_id=self.supplier,
            responsibility='Babysitting Idiots'
        )

        self.salesman_delete_url = reverse(
            'salesman_delete',
            kwargs={'salesman_id': self.salesman.salesman_id}
        )

        return super().setUp()

    def test_admin_successfully_delete_salesman(self) -> None:
        """
        Ensure admin can delete salesman successfully
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.salesman_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data salesman berhasil dihapus')
        self.assertEqual(len(Customer.objects.all()), 0)

    def test_nonlogin_user_failed_to_delete_salesman(self) -> None:
        """
        Ensure non-login user cannot delete salesman
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.salesman_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_delete_salesman(self) -> None:
        """
        Ensure non-admin user cannot delete salesman
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.salesman_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_delete_nonexist_salesman(self) -> None:
        """
        Ensure admin cannot to delete non-exist salesman
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('salesman_delete', kwargs={'salesman_id': 86591}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data salesman tidak ditemukan')
