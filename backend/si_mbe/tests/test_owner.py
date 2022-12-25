from datetime import date, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from si_mbe.models import (Brand, Category, Customer, Logs, Profile, Restock,
                           Restock_detail, Sales, Sales_detail, Salesman,
                           Sparepart, Storage, Supplier)
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
        self.assertEqual(response.data, {
                'sales_id': self.sales.sales_id,
                'admin': 'Richard Rider',
                'created_at': self.created_at_1.strftime('%d-%m-%Y %H:%M:%S'),
                'updated_at': self.updated_at_1.strftime('%d-%m-%Y %H:%M:%S'),
                'customer': self.sales.customer_id.name,
                'contact': self.sales.customer_id.contact,
                'is_paid_off': False,
                'deposit': str(self.sales.deposit),
                'content': [
                    {
                        'sales_detail_id': self.sales_details_1.sales_detail_id,
                        'sparepart': self.spareparts[2].name,
                        'quantity': 15,
                        'is_workshop': False
                    },
                    {
                        'sales_detail_id': self.sales_details_2.sales_detail_id,
                        'sparepart': self.spareparts[0].name,
                        'quantity': 10,
                        'is_workshop': False
                    },
                    {
                        'sales_detail_id': self.sales_details_3.sales_detail_id,
                        'sparepart': self.spareparts[1].name,
                        'quantity': 20,
                        'is_workshop': True
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
            address='Planet Taa',
            contact='084894564563',
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
            address='Planet Narkina, Outer Rim',
            contact='084894564563'
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
        cls.customer = Customer.objects.create(
            name='Caduceus Clay',
            contact='085456105311'
        )

        Sales.objects.create(
            customer_id=cls.customer
        )

        return super().setUpTestData()

    def test_owner_successfully_access_owner_dashboard(self) -> None:
        """
        Ensure owner can access owner dashboard
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.owner_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sales_today'], 1)

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
