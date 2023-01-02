from calendar import monthrange
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from si_mbe.models import (Brand, Category, Customer, Logs, Mechanic, Profile,
                           Restock, Restock_detail, Sales, Sales_detail,
                           Salesman, Service, Service_action,
                           Service_sparepart, Sparepart, Storage, Supplier)
from si_mbe.tests.test_admin import SetTestCase


class SalesReportListTestCase(APITestCase):
    sales_report_url = reverse('sales_report_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and owner user
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Profile.objects.create(user_id=cls.user, role='A', name='Richard Rider')

        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Profile.objects.create(user_id=cls.owner, role='P')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Dragon Steel')

        # Setting up storage data
        cls.storage = Storage.objects.create(code='EP-12')

        # Setting up category data
        cls.category = Category.objects.create(name='Book')

        # Setting up sparepart data and getting their object
        for i in range(3):
            Sparepart.objects.create(
                name=f'Cosmere B-{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Fantasy',
                sparepart_type='Ori',
                price=5400000,
                workshop_price=5300000,
                install_price=5500000,
                brand_id=cls.brand,
                storage_id=cls.storage,
                category_id=cls.category
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up customer data
        cls.customer_1 = Customer.objects.create(
            name='Hoid',
            contact='085456105311'
        )
        cls.customer_2 = Customer.objects.create(
            name='Vasheer',
            contact='085456102341'
        )

        # Setting up sales data and getting their object
        cls.sales_1 = Sales.objects.create(
                customer_id=cls.customer_1,
                user_id=cls.user,
            )
        cls.sales_2 = Sales.objects.create(
                customer_id=cls.customer_2,
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
                'customer': self.sales_1.customer_id.name,
                'contact': self.sales_1.customer_id.contact,
                'total_price_sales': 0,
                'is_paid_off': False,
                'deposit': str(self.sales_1.deposit)
            },
            {
                'sales_id': self.sales_2.sales_id,
                'admin': 'Richard Rider',
                'created_at': self.created_at_2.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': self.updated_at_2.strftime('%d-%m-%Y %H:%M:%S'),
                'customer': self.sales_2.customer_id.name,
                'contact': self.sales_2.customer_id.contact,
                'total_price_sales': 0,
                'is_paid_off': True,
                'deposit': str(self.sales_2.deposit)
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
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Profile.objects.create(user_id=cls.user, role='A', name='Richard Rider')

        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Profile.objects.create(user_id=cls.owner, role='P')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Steins Gate')

        # Setting up storage data
        cls.storage = Storage.objects.create(code='JD-24')

        # Setting up category data
        cls.category = Category.objects.create(name='Machine')

        # Setting up sparepart data and getting their object
        for i in range(3):
            Sparepart.objects.create(
                name=f'el psy congroo S-{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Time Machine',
                sparepart_type='DIY',
                price=5400000,
                workshop_price=5300000,
                install_price=5500000,
                brand_id=cls.brand,
                category_id=cls.category,
                storage_id=cls.storage
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up customer data
        cls.customer = Customer.objects.create(
            name='Rintaro Okabe',
            contact='084468104651',
        )

        # Setting up sales data and getting their object
        cls.sales = Sales.objects.create(
                customer_id=cls.customer,
                user_id=cls.user,
            )

        # Getting newly added sales it's sales_id then set it to kwargs in reverse url
        cls.sales_report_detail_url = reverse('sales_report_detail', kwargs={'sales_id': cls.sales.sales_id})

        # Setting up sales detail data and getting their object
        cls.sales_details_1 = Sales_detail.objects.create(
            quantity=15,
            is_workshop=False,
            sales_id=cls.sales,
            sparepart_id=cls.spareparts[2]
        )
        cls.sales_details_2 = Sales_detail.objects.create(
            quantity=10,
            is_workshop=False,
            sales_id=cls.sales,
            sparepart_id=cls.spareparts[0]
        )
        cls.sales_details_3 = Sales_detail.objects.create(
            quantity=20,
            is_workshop=True,
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
                'sales_id': self.sales.sales_id,
                'admin': 'Richard Rider',
                'created_at': self.created_at_1.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': self.updated_at_1.strftime('%d-%m-%Y %H:%M:%S'),
                'customer': self.sales.customer_id.name,
                'contact': self.sales.customer_id.contact,
                'total_price_sales': 241000000,
                'is_paid_off': False,
                'deposit': str(self.sales.deposit),
                'content': [
                    {
                        'sales_detail_id': self.sales_details_1.sales_detail_id,
                        'sparepart': self.spareparts[2].name,
                        'quantity': 15,
                        'is_workshop': False,
                        'total_price': 81000000
                    },
                    {
                        'sales_detail_id': self.sales_details_2.sales_detail_id,
                        'sparepart': self.spareparts[0].name,
                        'quantity': 10,
                        'is_workshop': False,
                        'total_price': 54000000
                    },
                    {
                        'sales_detail_id': self.sales_details_3.sales_detail_id,
                        'sparepart': self.spareparts[1].name,
                        'quantity': 20,
                        'is_workshop': True,
                        'total_price': 106000000
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

    def test_owner_failed_to_access_non_exist_sales_report_detail(self) -> None:
        """
        Ensure owner user cannot access non exist sales report detail
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(reverse('sales_report_detail', kwargs={'sales_id': 930514}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data penjualan tidak ditemukan')


class RestockReportTestCase(APITestCase):
    restock_report_url = reverse('restock_report_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and owner user
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Profile.objects.create(user_id=cls.user, role='A', name='Richard Rider')

        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Profile.objects.create(user_id=cls.owner, role='P')

        # Setting up brand
        cls.brand = Brand.objects.create(name='Cosmic Being')

        # Setting up storage data
        cls.storage = Storage.objects.create(code='FF-20')

        # Setting up category data
        cls.category = Category.objects.create(name='Creature')

        # Setting up supplier
        cls.supplier = Supplier.objects.create(
            name='Galactus',
            contact='084894564563',
            rekening_number='8468464056156',
            rekening_name='Galan',
            rekening_bank='Bank Taa'
        )

        # Setting up salesman
        cls.salesman = Salesman.objects.create(
            name='Galan',
            contact='084523015663',
            supplier_id=cls.supplier
        )

        # Setting up sparepart data and getting their object
        for i in range(3):
            Sparepart.objects.create(
                name=f'Herald {i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Cosmic Energy',
                sparepart_type='Bio',
                price=4700000,
                workshop_price=4620000,
                install_price=5500000,
                brand_id=cls.brand,
                category_id=cls.category,
                storage_id=cls.storage
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up restock data and getting their object
        for i in range(2):
            Restock.objects.create(
                no_faktur=f'URH45/28394/2022-N{i}D',
                due_date=date(2023, 4, 13),
                supplier_id=cls.supplier,
                is_paid_off=False,
                user_id=cls.user,
                salesman_id=cls.salesman
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
                'total_restock_cost': 0,
                'is_paid_off': False,
                'deposit': str(self.restocks[0].deposit),
                'due_date': self.restocks[0].due_date.strftime('%d-%m-%Y'),
                'supplier': self.supplier.name,
                'supplier_contact': self.supplier.contact,
                'salesman': self.restocks[0].salesman_id.name,
                'salesman_contact': self.restocks[0].salesman_id.contact
            },
            {
                'restock_id': self.restocks[1].restock_id,
                'admin': 'Richard Rider',
                'created_at': self.created_at_2.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': self.updated_at_2.strftime('%d-%m-%Y %H:%M:%S'),
                'no_faktur': self.restocks[1].no_faktur,
                'total_restock_cost': 0,
                'is_paid_off': False,
                'deposit': str(self.restocks[1].deposit),
                'due_date': self.restocks[1].due_date.strftime('%d-%m-%Y'),
                'supplier': self.supplier.name,
                'supplier_contact': self.supplier.contact,
                'salesman': self.restocks[1].salesman_id.name,
                'salesman_contact': self.restocks[1].salesman_id.contact
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
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Profile.objects.create(user_id=cls.user, role='A', name='Richard Rider')

        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Profile.objects.create(user_id=cls.owner, role='P')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Galactic Empire')

        # Setting up storage data
        cls.storage = Storage.objects.create(code='DS-01')

        # Setting up category data
        cls.category = Category.objects.create(name='Connector')

        # Setting up supplier
        cls.supplier = Supplier.objects.create(
            name='narkina 5',
            contact='084894564563',
            rekening_number='846668686404001',
            rekening_name='Kino Loy',
            rekening_bank='Bank Empire'
        )

        # Setting up salesman data
        cls.salesman = Salesman.objects.create(
            name='Kino Loy',
            contact='084523015663',
            supplier_id=cls.supplier
        )

        # Setting up sparepart data and getting their object
        for i in range(3):
            Sparepart.objects.create(
                name=f'Lens Spine D-{i}',
                partnumber=f'0Y3AD-FY{i}',
                quantity=50,
                motor_type='Deathstar',
                sparepart_type='OEM',
                price=4700000,
                workshop_price=4620000,
                install_price=5500000,
                brand_id=cls.brand,
                category_id=cls.category,
                storage_id=cls.storage
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up restock data and getting their object
        cls.restock = Restock.objects.create(
                no_faktur=f'URH45/28394/2022-N{i}D',
                due_date=date(2023, 4, 13),
                supplier_id=cls.supplier,
                is_paid_off=False,
                user_id=cls.user,
                salesman_id=cls.salesman
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
        Ensure owner can get restock report detail
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
                'total_restock_cost': 1395000000,
                'is_paid_off': False,
                'deposit': str(self.restock.deposit),
                'due_date': self.restock.due_date.strftime('%d-%m-%Y'),
                'supplier': self.supplier.name,
                'supplier_contact': self.supplier.contact,
                'salesman': self.restock.salesman_id.name,
                'salesman_contact': self.restock.salesman_id.contact,
                'content': [
                    {
                        'restock_detail_id': self.restock_detail_1.restock_detail_id,
                        'sparepart': self.spareparts[2].name,
                        'individual_price':'5000000',
                        'quantity': 200,
                        'total_price': 1000000000
                    },
                    {
                        'restock_detail_id': self.restock_detail_2.restock_detail_id,
                        'sparepart': self.spareparts[0].name,
                        'individual_price':'400000',
                        'quantity': 500,
                        'total_price': 200000000
                    },
                    {
                        'restock_detail_id': self.restock_detail_3.restock_detail_id,
                        'sparepart': self.spareparts[1].name,
                        'individual_price':'650000',
                        'quantity': 300,
                        'total_price': 195000000
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

    def test_owner_failed_to_access_non_exist_restock_report_detail(self) -> None:
        """
        Ensure owner user cannot access non exist restock report detail
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(reverse('restock_report_detail', kwargs={'restock_id': 930514}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data pengadaan tidak ditemukan')


class LogTestCase(APITestCase):
    log_url = reverse('log')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and owner user
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Profile.objects.create(user_id=cls.user, role='A', name='Richard Rider')

        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Profile.objects.create(user_id=cls.owner, role='P')

        cls.log_1 = Logs.objects.create(
            table='Sales',
            operation='R',
            user_id=cls.user
        )
        cls.log_2 = Logs.objects.create(
            table='Sparepart',
            operation='E',
            user_id=cls.user
        )

        cls.time_1 = cls.log_1.log_at + timedelta(hours=7)
        cls.time_2 = cls.log_2.log_at + timedelta(hours=7)

        return super().setUpTestData()

    def test_owner_successfully_access_log(self) -> None:
        """
        Ensure owner can access log successfully
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.log_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'], [
            {
                'log_id': self.log_1.log_id,
                'log_at': self.time_1.strftime('%d-%m-%Y %H:%M:%S'),
                'user': self.log_1.user_id.profile.name,
                'table': self.log_1.table,
                'operation': self.log_1.get_operation_display()
            },
            {
                'log_id': self.log_2.log_id,
                'log_at': self.time_2.strftime('%d-%m-%Y %H:%M:%S'),
                'user': self.log_2.user_id.profile.name,
                'table': self.log_2.table,
                'operation': self.log_2.get_operation_display()
            }
        ])

    def test_nonlogin_user_failed_to_access_log(self) -> None:
        """
        Ensure non-login user cannot access_log
        """
        response = self.client.get(self.log_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_access_log(self) -> None:
        """
        Ensure non-owner user cannot access log
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.log_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class OwnerDashboardTestCase(SetTestCase):
    owner_dashboard_url = reverse('owner_dashboard')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up customer
        cls.customer_1 = Customer.objects.create(
            name='Caduceus Clay',
            contact='085456105311'
        )
        cls.customer_2 = Customer.objects.create(
            name='Dick Grayson',
            contact='085116666556'
        )

        # Setting up sparepart
        cls.sparepart = Sparepart.objects.create(
            name='Holder',
            partnumber='9HF-1',
            quantity=80,
            price=12000,
            install_price=14500,
            workshop_price=11000,
            motor_type='Yamaha',
            sparepart_type='Additions',
        )

        # Setting up sales data
        cls.sales_1 = Sales.objects.create(
            customer_id=cls.customer_1
        )
        cls.sales_2 = Sales.objects.create(
            customer_id=cls.customer_2
        )

        Sales_detail.objects.create(
            sales_id=cls.sales_1,
            quantity=8,
            sparepart_id=cls.sparepart
        )
        Sales_detail.objects.create(
            sales_id=cls.sales_2,
            quantity=23,
            sparepart_id=cls.sparepart,
            is_workshop=True
        )

        # Setting up service data
        cls.service_1 = Service.objects.create(
            police_number='B 2983 A',
            discount=5000,
            motor_type='Honda',
            customer_id=cls.customer_1
        )
        cls.service_2 = Service.objects.create(
            police_number='B 2983 A',
            discount=8500,
            motor_type='Honda',
            customer_id=cls.customer_2
        )

        Service_action.objects.create(
            service_id=cls.service_1,
            name='Cuci Motor',
            cost=50000
        )
        Service_sparepart.objects.create(
            service_id=cls.service_1,
            quantity=2,
            sparepart_id=cls.sparepart
        )

        Service_action.objects.create(
            service_id=cls.service_2,
            name='Pompa',
            cost=35000
        )
        Service_sparepart.objects.create(
            service_id=cls.service_2,
            quantity=10,
            sparepart_id=cls.sparepart
        )

        # Setting up restock / expenditure data
        cls.restock_1 = Restock.objects.create(
            no_faktur='GHFG-313',
            due_date=date(2023, 1, 4)
        )
        cls.restock_2 = Restock.objects.create(
            no_faktur='GHFG-313',
            due_date=date(2023, 1, 8)
        )

        Restock_detail.objects.create(
            restock_id=cls.restock_1,
            quantity=256,
            individual_price=17000,
            sparepart_id=cls.sparepart
        )
        Restock_detail.objects.create(
            restock_id=cls.restock_1,
            quantity=137,
            individual_price=9500
        )
        Restock_detail.objects.create(
            restock_id=cls.restock_2,
            quantity=312,
            individual_price=11500,
            sparepart_id=cls.sparepart
        )

        return super().setUpTestData()

    def test_owner_successfully_access_owner_dashboard(self) -> None:
        """
        Ensure owner can access owner dashboard
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.owner_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['revenue_in_month']),
            monthrange(year=date.today().year, month=date.today().month)[1]
        )
        self.assertEqual(response.data['total_revenue_today'], 594500)
        self.assertEqual(response.data['sales_revenue_today'], 349000)
        self.assertEqual(response.data['service_revenue_today'], 245500)
        self.assertEqual(response.data['sales_count_today'], 2)
        self.assertEqual(response.data['service_count_today'], 2)
        self.assertEqual(response.data['expenditure_today'], 9241500)

    def test_nonlogin_user_failed_to_access_owner_dashboard(self) -> None:
        """
        Ensure non-login user cannot access owner dashboard
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.owner_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_access_owner_dashboard(self) -> None:
        """
        Ensure non-owner user cannot access owner dashboard
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.owner_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class AdminListTestCase(SetTestCase):
    admin_list_url = reverse('admin_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up additional admin data
        cls.admin = User.objects.create_user(
            username='nottthebrave',
            password='Veth',
            email='samreigel@yahoo.com'
        )

        Profile.objects.create(user_id=cls.admin, role='A', name='Nott The Brave', contact='085360467830')

        return super().setUpTestData()

    def test_owner_successfully_access_admin_list(self) -> None:
        """
        Ensure owner can access owner dashboard
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.admin_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)

    def test_nonlogin_user_failed_to_access_admin_list(self) -> None:
        """
        Ensure non-login user cannot access admin list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.admin_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_access_admin_list(self) -> None:
        """
        Ensure non-owner user cannot access admin list
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.admin_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class AdminAddTestCase(SetTestCase):
    admin_add_url = reverse('admin_add')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.data = {
            'username': 'samalexander',
            'name': 'Sam Alexander',
            'password': 'NewNova1',
            'password_2': 'NewNova1',
            'email': 'newnovahere@gmail.com',
            'contact': '084654464866',
            'address': 'Jln Stanford School',
        }

        cls.data_wrong_password = {
            'username': 'samalexander',
            'name': 'Sam Alexander',
            'password': 'NewNova1',
            'password_2': 'NewWarriors',
            'email': 'newnovahere@gmail.com',
            'contact': '084654464866',
            'address': 'Jln Stanford School',
        }

        cls.incomplete_data = {
            'username': 'abinshurr',
            'name': 'Abin Shurr',
            'contact': '085231313101'
        }
        return super().setUpTestData()

    def test_owner_successfully_add_admin(self) -> None:
        """
        Ensure owner can add user admin
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.admin_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(User.objects.filter(profile__role='A')), 2)

    def test_nonlogin_user_failed_to_add_admin(self) -> None:
        """
        Ensure non-login user cannot add admin
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.admin_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_add_admin(self) -> None:
        """
        Ensure non-owner user cannot add admin
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.admin_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_owner_failed_to_add_admin_with_wrong_password(self) -> None:
        """
        Ensure owner cannot add admin with wrong password
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.admin_add_url, self.data_wrong_password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Password dan Konfirmasi Password Berbeda')
        self.assertEqual(len(User.objects.filter(profile__role='A')), 1)

    def test_owner_failed_to_add_admin_with_incomplete_empty(self) -> None:
        """
        Ensure owner cannot add admin with incomplete empty
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.admin_add_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data admin tidak sesuai / tidak lengkap')

    def test_owner_failed_to_add_admin_with_incomplete_data(self) -> None:
        """
        Ensure owner cannot add admin with incomplete data
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.admin_add_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data admin tidak sesuai / tidak lengkap')


class AdminUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up additional admin data
        cls.admin = User.objects.create_user(
            username='arthagan',
            password='feywildsarchfey',
            email='arthagan@hotmail.com'
        )

        Profile.objects.create(user_id=cls.admin, role='A', name='Arthagan', contact='088526446044')

        cls.admin_update_url = reverse('admin_update', kwargs={'pk': cls.admin.pk})

        cls.data = {
            'username': 'thetraveller',
            'name': 'The Traveller',
            'email': 'thetraveller@hotmail.com',
            'contact': '086501651011',
            'address': 'Jln Fey Wilds'
        }

        cls.incomplete_data = {
            'username': 'moonkinds',
            'name': 'Moon Walker',
            'contact': '086484560466'
        }

        return super().setUpTestData()

    def test_owner_successfully_update_admin(self) -> None:
        """
        Ensure owner can update admin
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.admin_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Admin berhasil dirubah')
        self.assertEqual(response.data['username'], self.data['username'])
        self.assertEqual(response.data['email'], self.data['email'])
        self.assertEqual(response.data['contact'], self.data['contact'])
        self.assertEqual(response.data['name'], self.data['name'])
        self.assertEqual(response.data['address'], self.data['address'])

    def test_nonlogin_user_failed_to_update_admin(self) -> None:
        """
        Ensure non-login user cannot update admin
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.admin_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_update_admin(self) -> None:
        """
        Ensure non-owner user cannot update admin
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.admin_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_owner_failed_to_update_non_exist_admin(self) -> None:
        """
        Ensure owner user cannot update non exist admin
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(
            reverse('admin_update', kwargs={'pk': 64505}),
            self.data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data admin tidak ditemukan')

    def test_owner_failed_to_update_admin_with_empty_data(self) -> None:
        """
        Ensure owner user cannot update admin with empty data
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.admin_update_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data admin tidak sesuai / tidak lengkap')

    def test_owner_failed_to_update_admin_with_incomplete_data(self) -> None:
        """
        Ensure owner user cannot update admin with incomplete data
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.admin_update_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data admin tidak sesuai / tidak lengkap')


class AdminDeleteTestCase(SetTestCase):
    def setUp(self) -> None:
        # Setting up additional admin data
        self.admin = User.objects.create_user(
            username='lucien',
            password='theeyeofnine',
            email='nanagon@hotmail.com'
        )
        Profile.objects.create(user_id=self.admin, role='A', name='Lucien', contact='081086016510')

        self.admin_delete_url = reverse('admin_delete', kwargs={'pk': self.admin.pk})

        return super().setUp()

    def test_owner_successfully_delete_admin(self) -> None:
        """
        Ensure owner can delete admin (is_active=False)
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.admin_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data admin berhasil dihapus')
        self.assertEqual(len(User.objects.filter(profile__role='A')), 2)
        self.assertEqual(len(User.objects.filter(profile__role='A', is_active=True)), 1)

    def test_nonlogin_user_failed_to_delete_admin(self) -> None:
        """
        Ensure non-login user cannot delete admin
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.admin_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_delete_admin(self) -> None:
        """
        Ensure non-owner user cannot delete admin
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.admin_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_owner_failed_to_delete_non_exist_admin(self) -> None:
        """
        Ensure owner user cannot delete non exist admin
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(reverse('admin_delete', kwargs={'pk': 43852}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data admin tidak ditemukan')


class ServiceReportTestCase(SetTestCase):
    service_report_url = reverse('service_report_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up additional admin data
        cls.admin = User.objects.create_user(
            username='jester',
            password='littlesaphire',
            email='jester@hotmail.com'
        )
        Profile.objects.create(
            user_id=cls.admin,
            role='A',
            name='Jester Lavorre',
            contact='081086016510',
            address='Nicrodanas'
        )

        # Setting up mechanic data
        cls.mechanic = Mechanic.objects.create(
            name='Percy Deloro The Third',
            contact='086206164404',
            address='Whitestone'
        )

        # Setting up customer data
        cls.customer = Customer.objects.create(
            name='Scanlant Shorthalt',
            contact='082541684051',
        )

        cls.service = Service.objects.create(
            police_number='B 1293 A',
            motor_type='Beneli',
            deposit=500000,
            discount=20000,
            user_id=cls.admin,
            mechanic_id=cls.mechanic,
            customer_id=cls.customer
        )

        # Setting up time data for test comparison
        cls.created_at = cls.service.created_at + timedelta(hours=7)
        cls.updated_at = cls.service.updated_at + timedelta(hours=7)

        # Setting up service_action and service_sparepart
        Service_action.objects.create(
            name='Angkat Motor',
            cost='120000',
            service_id=cls.service
        )

        return super().setUpTestData()

    def test_owner_successfully_access_service_report_list(self) -> None:
        """
        Ensure owner can access service report list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.service_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['results'], [
            {
                'service_id': self.service.service_id,
                'admin': self.service.user_id.profile.name,
                'created_at': self.created_at.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': self.updated_at.strftime('%d-%m-%Y %H:%M:%S'),
                'police_number': self.service.police_number,
                'mechanic': self.service.mechanic_id.name,
                'customer': self.service.customer_id.name,
                'customer_contact': self.service.customer_id.contact,
                'total_price_of_service': 100000,
                'is_paid_off': self.service.is_paid_off,
                'deposit': str(self.service.deposit),
                'discount': str(self.service.discount)
            }
        ])

    def test_nonlogin_user_failed_to_access_service_report_list(self) -> None:
        """
        Ensure non-login user cannot access service report list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.service_report_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_access_service_report_list(self) -> None:
        """
        Ensure non-owner user cannot access service report list
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.service_report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class ServiceReportDetailTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up additional admin data
        cls.admin = User.objects.create_user(
            username='jester',
            password='littlesaphire',
            email='jester@hotmail.com'
        )
        Profile.objects.create(
            user_id=cls.admin,
            role='A',
            name='Jester Lavorre',
            contact='081086016510',
            address='Nicrodanas'
        )

        # Setting up mechanic data
        cls.mechanic = Mechanic.objects.create(
            name='Percy Deloro The Third',
            contact='086206164404',
            address='Whitestone'
        )

        # Setting up customer data
        cls.customer = Customer.objects.create(
            name='Scanlant Shorthalt',
            contact='082541684051',
        )

        cls.service = Service.objects.create(
            police_number='B 1293 A',
            motor_type='Beneli',
            deposit=500000,
            discount=20000,
            user_id=cls.admin,
            mechanic_id=cls.mechanic,
            customer_id=cls.customer
        )

        cls.service_report_detail_url = reverse(
            'service_report_detail',
            kwargs={'service_id': cls.service.service_id}
        )

        # Setting up service actions
        cls.action_1 = Service_action.objects.create(
            name='Pompa Ban',
            cost='10000',
            service_id=cls.service
        )
        cls.action_2 = Service_action.objects.create(
            name='Bongkar Mesin',
            cost='400000',
            service_id=cls.service
        )
        cls.action_3 = Service_action.objects.create(
            name='Angkat Lampu',
            cost='300000',
            service_id=cls.service
        )

        # Setting up storage data
        cls.storage = Storage.objects.create(code='MN-9')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Lavish Chateau')

        # Setting up category data
        cls.category = Category.objects.create(name='Fodd')

        # Setting up sparepart data
        cls.sparepart = Sparepart.objects.create(
            name='Chorcoal Cupcake',
            partnumber='JFLJ23-Aj',
            quantity=50,
            motor_type='Humans',
            sparepart_type='Spices',
            price=105000,
            workshop_price=100000,
            install_price=110000,
            brand_id=cls.brand,
            category_id=cls.category,
            storage_id=cls.storage
        )

        # Setting up service sparepart
        cls.service_sparepart = Service_sparepart.objects.create(
            quantity=2,
            service_id=cls.service,
            sparepart_id=cls.sparepart
        )

        # Setting up time data for test comparison
        cls.created_at = cls.service.created_at + timedelta(hours=7)
        cls.updated_at = cls.service.updated_at + timedelta(hours=7)

        return super().setUpTestData()

    def test_owner_successfully_access_service_report_detail(self) -> None:
        """
        Ensure owner can access service report detail
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.service_report_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'service_id': self.service.service_id,
            'admin': self.service.user_id.profile.name,
            'created_at': self.created_at.strftime('%d-%m-%Y %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%d-%m-%Y %H:%M:%S'),
            'police_number': self.service.police_number,
            'mechanic': self.service.mechanic_id.name,
            'customer': self.service.customer_id.name,
            'customer_contact': self.service.customer_id.contact,
            'total_price_of_service': 910000,
            'is_paid_off': self.service.is_paid_off,
            'deposit': str(self.service.deposit),
            'discount': str(self.service.discount),
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
                    'service_sparepart_id': self.service_sparepart.service_sparepart_id,
                    'sparepart': self.service_sparepart.sparepart_id.name,
                    'quantity': self.service_sparepart.quantity,
                    'total_price':
                    int(self.service_sparepart.sparepart_id.install_price * self.service_sparepart.quantity)
                }
            ]
        })

    def test_nonlogin_user_failed_to_access_service_report_detail(self) -> None:
        """
        Ensure non-login user cannot access service report detail
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.service_report_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_access_service_report_detail(self) -> None:
        """
        Ensure non-owner user cannot access service report detail
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.service_report_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_owner_failed_to_access_non_exist_service_report_detail(self) -> None:
        """
        Ensure owner user cannot access non exist service report detail
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(reverse('service_report_detail', kwargs={'service_id': 930514}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data servis tidak ditemukan')


class MechanicListTestCase(SetTestCase):
    mechanic_url = reverse('mechanic_list')

    @classmethod
    def setUpTestData(cls) -> None:
        # setting up mechanic data
        cls.mechanic = Mechanic.objects.create(
            name='The Third Fleet',
            contact='085132135051',
            address='Jl Port Domali'
        )
        Mechanic.objects.create(
            name='The Fifth Fleet',
            contact='082351351010',
            address='Jl Rexxentrum'
        )

        return super().setUpTestData()

    def test_owner_successfully_access_mechanic_list(self) -> None:
        """
        Ensure owner can get mechanic list successfully
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.mechanic_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 2)
        self.assertEqual(response.data['results'][0]['name'], self.mechanic.name)
        self.assertEqual(response.data['results'][0]['contact'], self.mechanic.contact)
        self.assertEqual(response.data['results'][0]['address'], self.mechanic.address)

    def test_nonlogin_user_failed_to_access_mechanic_list(self) -> None:
        """
        Ensure non-login user cannot access mechanic list
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.mechanic_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_access_mechanic_list(self) -> None:
        """
        Ensure non-owner user cannot access mechanic list
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.mechanic_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_owner_successfully_searching_mechanic_with_result(self) -> None:
        """
        Ensure owner who searching mechanic with correct keyword get correct result
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(reverse('mechanic_list') + f'?q={self.mechanic.name}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 1)
        self.assertEqual(response.data['results'], [
            {
                'mechanic_id': self.mechanic.mechanic_id,
                'name': self.mechanic.name,
                'contact': self.mechanic.contact,
                'address': self.mechanic.address
            }
        ])

    def test_owner_successfully_searching_mechanic_without_result(self) -> None:
        """
        Ensure owner search mechanic that doesn't exist get empty result
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(reverse('mechanic_list') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count_item'], 0)
        self.assertEqual(response.data['message'], 'Mekanik yang dicari tidak ditemukan')


class MechanicAddTestCase(SetTestCase):
    mechanic_add_url = reverse('mechanic_add')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up input data
        cls.data = {
            'name': 'Deacon',
            'contact': '085132135051',
            'address': 'Jl Railroad Boston'
        }
        cls.incomplete_data = {
            'address': 'Jl Railroad Boston'
        }

        return super().setUpTestData()

    def test_admin_successfully_add_mechanic(self) -> None:
        """
        Ensure admin can add new mechanic successfully
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.mechanic_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Data mekanik berhasil ditambah')
        self.assertEqual(response.data['name'], self.data['name'])
        self.assertEqual(response.data['contact'], self.data['contact'])
        self.assertEqual(response.data['address'], self.data['address'])

    def test_nonlogin_user_failed_to_add_new_mechanic(self) -> None:
        """
        Ensure non-login user cannot add new mechanic
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.post(self.mechanic_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonadmin_user_failed_to_add_new_mechanic(self) -> None:
        """
        Ensure non-admin user cannot add new mechanic
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.mechanic_add_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_owner_failed_to_add_mechanic_with_empty_data(self) -> None:
        """
        Ensure owner cannot add mechanic with empty data / input
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.mechanic_add_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data mekanik tidak sesuai / tidak lengkap')

    def test_owner_failed_to_add_mechanic_with_incomplete_data(self) -> None:
        """
        Ensure owner cannot add mechanic with incomplete data / input
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.mechanic_add_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data mekanik tidak sesuai / tidak lengkap')


class MechanicUpdateTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting mechanic data
        cls.mechanic = Mechanic.objects.create(
            name='The Crick',
            contact='083260466406',
            address='Jl Roshan'
        )

        cls.mechanic_update_url = reverse(
            'mechanic_update',
            kwargs={'mechanic_id': cls.mechanic.mechanic_id}
        )

        # Setting up input data
        cls.data = {
            'name': 'Essek',
            'contact': '086084501500',
            'address': 'Jl Roshan'
        }
        cls.incomplete_data = {
            'address': 'Jl Railroad Boston'
        }

        return super().setUpTestData()

    def test_owner_successfully_update_mechanic(self) -> None:
        """
        Ensure owner can update mechanic successfully
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.mechanic_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Data mekanik berhasil dirubah')
        self.assertEqual(response.data['name'], self.data['name'])
        self.assertEqual(response.data['contact'], self.data['contact'])
        self.assertEqual(response.data['address'], self.data['address'])

    def test_nonlogin_user_failed_to_update_mechanic(self) -> None:
        """
        Ensure non-login user cannot update mechanic
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.put(self.mechanic_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_update_mechanic(self) -> None:
        """
        Ensure non-owner user cannot update mechanic
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.mechanic_update_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_owner_failed_to_update_nonexist_mechanic(self) -> None:
        """
        Ensure owner cannot update non-exist mechanic
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(reverse('mechanic_update', kwargs={'mechanic_id': 526523}),
                                   self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data mekanik tidak ditemukan')

    def test_owner_failed_to_update_mechanic_with_empty_data(self) -> None:
        """
        Ensure owner cannot update data mechanic with empty data / input
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.mechanic_update_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data mekanik tidak sesuai / tidak lengkap')

    def test_owner_failed_to_update_mechanic_with_incomplete_data(self) -> None:
        """
        Ensure owner cannot update data mechanic with incomplete data / input
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.mechanic_update_url, self.incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Data mekanik tidak sesuai / tidak lengkap')


class MechanicDeleteTestCase(SetTestCase):
    def setUp(self) -> None:
        # Setting up storage data
        self.mechanic = Mechanic.objects.create(
            name='Jonathan Hickman',
            contact='086054056640',
            address='Jl Marvel'
        )

        self.mechanic_delete_url = reverse(
            'mechanic_delete',
            kwargs={'mechanic_id': self.mechanic.mechanic_id}
        )

        return super().setUp()

    def test_admin_successfully_delete_mechanic(self) -> None:
        """
        Ensure admin can delete mechanic successfully
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.mechanic_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Data mekanik berhasil dihapus')
        self.assertEqual(len(Customer.objects.all()), 0)

    def test_nonlogin_user_failed_to_delete_mechanic(self) -> None:
        """
        Ensure non-login user cannot delete mechanic
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.delete(self.mechanic_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_delete_mechanic(self) -> None:
        """
        Ensure non-owner user cannot delete mechanic
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.mechanic_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')

    def test_admin_failed_to_delete_nonexist_mechanic(self) -> None:
        """
        Ensure admin cannot to delete non-exist mechanic
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(reverse('mechanic_delete', kwargs={'mechanic_id': 86591}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data mekanik tidak ditemukan')
