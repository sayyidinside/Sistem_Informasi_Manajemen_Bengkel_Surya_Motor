from datetime import date, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from si_mbe.models import (Brand, Category, Customer, Logs, Mechanic, Profile,
                           Restock, Restock_detail, Sales, Sales_detail,
                           Salesman, Service, Service_action,
                           Service_sparepart, Sparepart, Supplier)
from si_mbe.tests.test_admin import SetTestCase


class SalesReportTestCase(APITestCase):
    sales_report_url = reverse('sales_report')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and owner user
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Profile.objects.create(user_id=cls.user, role='A', name='Richard Rider')

        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Profile.objects.create(user_id=cls.owner, role='P')

        # Setting up brand data
        cls.brand = Brand.objects.create(name='Dragon Steel')

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
                price=540000,
                workshop_price=530000,
                install_price=550000,
                brand_id=cls.brand,
                storage_code='HJF-502',
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
            contact='085456102341',
            is_workshop=True
        )

        # Setting up sales data and getting their object
        cls.sales_1 = Sales.objects.create(
                customer_id=cls.customer_1,
                user_id=cls.user,
                deposit=751000,
                discount=20000
            )
        cls.sales_2 = Sales.objects.create(
                customer_id=cls.customer_2,
                user_id=cls.user,
                discount=10000
            )

        Sales_detail.objects.create(
            sales_id=cls.sales_1,
            sparepart_id=cls.spareparts[0],
            quantity=5
        )
        Sales_detail.objects.create(
            sales_id=cls.sales_1,
            sparepart_id=cls.spareparts[1],
            quantity=2
        )
        Sales_detail.objects.create(
            sales_id=cls.sales_1,
            sparepart_id=cls.spareparts[2],
            quantity=7
        )
        Sales_detail.objects.create(
            sales_id=cls.sales_2,
            sparepart_id=cls.spareparts[0],
            quantity=30
        )
        Sales_detail.objects.create(
            sales_id=cls.sales_2,
            sparepart_id=cls.spareparts[1],
            quantity=40
        )

        cls.date = int(date.today().day) - 1

        return super().setUpTestData()

    def test_owner_successfully_access_sales_report(self) -> None:
        """
        Ensure owner can get sales report
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.sales_report_url)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate sales information per day table data
        self.assertEqual(response.data['sales_report'][self.date]['date'], date.today() + timedelta(hours=7))
        self.assertEqual(response.data['sales_report'][self.date]['sales_transaction'], 44630000)
        self.assertEqual(response.data['sales_report'][self.date]['sales_revenue'], 751000)
        self.assertEqual(response.data['sales_report'][self.date]['sales_count'], 2)

        self.assertEqual(response.data['sales_report'][self.date - 2]['date'],
                         date.today() - timedelta(days=2) + timedelta(hours=7))
        self.assertEqual(response.data['sales_report'][self.date - 2]['sales_transaction'], 0)
        self.assertEqual(response.data['sales_report'][self.date - 2]['sales_revenue'], 0)
        self.assertEqual(response.data['sales_report'][self.date - 2]['sales_count'], 0)

        # Validate total month informations
        self.assertEqual(response.data['sales_transaction_month'], 44630000)
        self.assertEqual(response.data['sales_revenue_month'], 751000)

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


class RestockReportTestCase(APITestCase):
    restock_report_url = reverse('restock_report')

    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up admin user and owner user
        cls.user = User.objects.create_user(username='richardrider', password='NovaPrimeAnnahilations')
        Profile.objects.create(user_id=cls.user, role='A', name='Richard Rider')

        cls.owner = User.objects.create_user(username='One Above All', password='TrueComicBookWriter')
        Profile.objects.create(user_id=cls.owner, role='P')

        # Setting up brand
        cls.brand = Brand.objects.create(name='Cosmic Being')

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
                storage_code='CSM-53100'
            )

        cls.spareparts = Sparepart.objects.all()

        # Setting up restock data and getting their object
        for i in range(2):
            Restock.objects.create(
                no_faktur=f'URH45/28394/2022-N{i}D',
                due_date=date(2023, 4, 13),
                is_paid_off=False,
                user_id=cls.user,
                salesman_id=cls.salesman,
                deposit=int(f'{i}1{i+3}00000')
            )

        cls.restocks = Restock.objects.all()

        Restock_detail.objects.create(
            restock_id=cls.restocks[0],
            sparepart_id=cls.spareparts[0],
            quantity=200,
            individual_price=15000
        )
        Restock_detail.objects.create(
            restock_id=cls.restocks[0],
            sparepart_id=cls.spareparts[1],
            quantity=100,
            individual_price=38000
        )
        Restock_detail.objects.create(
            restock_id=cls.restocks[0],
            sparepart_id=cls.spareparts[2],
            quantity=350,
            individual_price=2700
        )
        Restock_detail.objects.create(
            restock_id=cls.restocks[1],
            sparepart_id=cls.spareparts[0],
            quantity=200,
            individual_price=35200
        )
        Restock_detail.objects.create(
            restock_id=cls.restocks[1],
            sparepart_id=cls.spareparts[1],
            quantity=50,
            individual_price=62000
        )

        # Getting current date / day
        cls.date = int(date.today().day) - 1

        return super().setUpTestData()

    def test_owner_successfully_access_restock_report_list(self):
        """
        Ensure owner can get restock report list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.restock_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate restock information per day table data
        self.assertEqual(response.data['restock_report'][self.date]['date'], date.today() + timedelta(hours=7))
        self.assertEqual(response.data['restock_report'][self.date]['restock_transaction'], 17885000)
        self.assertEqual(response.data['restock_report'][self.date]['restock_cost'], 12700000)

        self.assertEqual(response.data['restock_report'][self.date - 2]['date'],
                         date.today() - timedelta(days=2) + timedelta(hours=7))
        self.assertEqual(response.data['restock_report'][self.date - 2]['restock_transaction'], 0)
        self.assertEqual(response.data['restock_report'][self.date - 2]['restock_cost'], 0)

        # Validate total month informations
        self.assertEqual(response.data['restock_transaction_month'], 17885000)
        self.assertEqual(response.data['restock_cost_month'], 12700000)

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
            sparepart_id=cls.sparepart
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
        self.assertEqual(response.data['total_revenue_today'], 617500)
        self.assertEqual(response.data['sales_revenue_today'], 372000)
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

    def test_owner_failed_to_add_admin_with_empty_data(self) -> None:
        """
        Ensure owner cannot add admin with empty data
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
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up additional admin data
        cls.admin = User.objects.create_user(
            username='lucien',
            password='theeyeofnine',
            email='nanagon@hotmail.com'
        )
        Profile.objects.create(user_id=cls.admin, role='A', name='Lucien', contact='081086016510')

        cls.admin_delete_url = reverse('admin_delete', kwargs={'pk': cls.admin.pk})
        return super().setUpTestData()

    def setUp(self) -> None:
        self.admin.is_active = True
        self.admin.save()

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
    service_report_url = reverse('service_report')

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

        # Setting up sparepart data and getting their object
        cls.sparepart = Sparepart.objects.create(
                name='Lightsong The Brave',
                partnumber='0Y3AD-FY',
                quantity=50,
                motor_type='Fantasy',
                sparepart_type='Ori',
                price=540000,
                workshop_price=530000,
                install_price=550000,
                storage_code='HJF-502',
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
            discount=53500,
            user_id=cls.admin,
            mechanic_id=cls.mechanic,
            customer_id=cls.customer
        )
        cls.service_2 = Service.objects.create(
            police_number='B 1293 A',
            motor_type='Beneli',
            deposit=6700000,
            discount=200000,
            user_id=cls.admin,
            mechanic_id=cls.mechanic,
            customer_id=cls.customer
        )

        # Setting up service_action and service_sparepart
        Service_action.objects.create(
            name='Angkat Motor',
            cost='325000',
            service_id=cls.service
        )
        Service_sparepart.objects.create(
            service_id=cls.service,
            sparepart_id=cls.sparepart,
            quantity=3
        )
        Service_action.objects.create(
            name='Tukar Tambah',
            cost='12000000',
            service_id=cls.service_2
        )

        cls.date = int(date.today().day) - 1

        return super().setUpTestData()

    def test_owner_successfully_access_service_report_list(self) -> None:
        """
        Ensure owner can access service report list
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.service_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate service information per day table data
        self.assertEqual(response.data['service_report'][self.date]['date'], date.today() + timedelta(hours=7))
        self.assertEqual(response.data['service_report'][self.date]['service_transaction'], 13721500)
        self.assertEqual(response.data['service_report'][self.date]['service_revenue'], 7200000)

        self.assertEqual(response.data['service_report'][self.date - 2]['date'],
                         date.today() - timedelta(days=2) + timedelta(hours=7))
        self.assertEqual(response.data['service_report'][self.date - 2]['service_transaction'], 0)
        self.assertEqual(response.data['service_report'][self.date - 2]['service_revenue'], 0)

        # Validate total month informations
        self.assertEqual(response.data['service_transaction_month'], 13721500)
        self.assertEqual(response.data['service_revenue_month'], 7200000)

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

    def test_owner_failed_to_searching_mechanic_without_result(self) -> None:
        """
        Ensure owner search mechanic that doesn't exist get empty result
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(reverse('mechanic_list') + '?q=random shit')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
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

    def test_owner_successfully_add_mechanic(self) -> None:
        """
        Ensure owner can add new mechanic successfully
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
        # Setting up mechanic data
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

    def test_owner_successfully_delete_mechanic(self) -> None:
        """
        Ensure owner can delete mechanic successfully
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

    def test_owner_failed_to_delete_nonexist_mechanic(self) -> None:
        """
        Ensure owner cannot to delete non-exist mechanic
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(reverse('mechanic_delete', kwargs={'mechanic_id': 86591}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Data mekanik tidak ditemukan')


class DownloadSalesReportTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up normal url and variable for testing
        cls.download_sales_report_url = reverse('sales_report_download')
        cls.year = date.today().year
        cls.month = date.today().month

        # Setting up date spesific url and variable for testing
        cls.year_input = date(2022, 2, 1).year
        cls.month_input = date(2022, 2, 1).month
        cls.date_spesific_download_sales_report_url = reverse('sales_report_download') +\
            f'?year={cls.year_input}&month={cls.month_input}'

        return super().setUpTestData()

    def test_owner_successfully_download_sales_report(self) -> None:
        """
        Ensure owner can download sales report pdf
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.download_sales_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response.filename, f'Laporan_Penjualan-{self.year}-{self.month}.pdf')

    def test_owner_successfully_download_sales_report_with_date_input(self) -> None:
        """
        Ensure owner can download date spesific sales report pdf based on owner input of date
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.date_spesific_download_sales_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response.filename, f'Laporan_Penjualan-{self.year_input}-{self.month_input}.pdf')

    def test_nonlogin_user_failed_to_download_sales_report(self) -> None:
        """
        Ensure non-login user cannot download sales report pdf
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.download_sales_report_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_download_sales_report(self) -> None:
        """
        Ensure non-owner user cannot download sales report pdf
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.download_sales_report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class DownloadRestockReportTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up normal url and variable for testing
        cls.download_restock_report_url = reverse('restock_report_download')
        cls.year = date.today().year
        cls.month = date.today().month

        # Setting up date spesific url and variable for testing
        cls.year_input = date(2022, 2, 1).year
        cls.month_input = date(2022, 2, 1).month
        cls.date_spesific_download_restock_report_url = reverse('restock_report_download') +\
            f'?year={cls.year_input}&month={cls.month_input}'

        return super().setUpTestData()

    def test_owner_successfully_download_restock_report(self) -> None:
        """
        Ensure owner can download restock report pdf
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.download_restock_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response.filename, f'Laporan_Pengadaan-{self.year}-{self.month}.pdf')

    def test_owner_successfully_download_restock_report_with_date_input(self) -> None:
        """
        Ensure owner can download date spesific restock report pdf based on owner input of date
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.date_spesific_download_restock_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response.filename, f'Laporan_Pengadaan-{self.year_input}-{self.month_input}.pdf')

    def test_nonlogin_user_failed_to_download_restock_report(self) -> None:
        """
        Ensure non-login user cannot download restock report pdf
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.download_restock_report_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_download_restock_report(self) -> None:
        """
        Ensure non-owner user cannot download restock report pdf
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.download_restock_report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')


class DownloadServiceTestCase(SetTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up normal url and variable for testing
        cls.download_service_report_url = reverse('service_report_download')
        cls.year = date.today().year
        cls.month = date.today().month

        # Setting up date spesific url and variable for testing
        cls.year_input = date(2022, 2, 1).year
        cls.month_input = date(2022, 2, 1).month
        cls.date_spesific_download_service_report_url = reverse('service_report_download') +\
            f'?year={cls.year_input}&month={cls.month_input}'

        return super().setUpTestData()

    def test_owner_successfully_download_service_report(self) -> None:
        """
        Ensure owner can download service report pdf
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.download_service_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response.filename, f'Laporan_Servis-{self.year}-{self.month}.pdf')

    def test_owner_successfully_download_restockservice_with_date_input(self) -> None:
        """
        Ensure owner can download date spesific service report pdf based on owner input of date
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.date_spesific_download_service_report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response.filename, f'Laporan_Servis-{self.year_input}-{self.month_input}.pdf')

    def test_nonlogin_user_failed_to_download_service_report(self) -> None:
        """
        Ensure non-login user cannot download service report pdf
        """
        self.client.force_authenticate(user=None, token=None)
        response = self.client.get(self.download_service_report_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Silahkan login terlebih dahulu untuk mengakses fitur ini')

    def test_nonowner_user_failed_to_download_service_report(self) -> None:
        """
        Ensure non-owner user cannot download service report pdf
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.download_service_report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Akses ditolak')
