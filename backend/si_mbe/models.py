from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
from si_mbe.validators import validate_image_size

# Create your models here.


# Profile tabel is extended of user tabel to give each user their perpective informations
class Profile(models.Model):
    user_id = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    name = models.CharField(max_length=30, default='')
    contact = models.CharField(max_length=13, default='')
    address = models.CharField(max_length=50, default='')

    class Roles(models.TextChoices):
        PEMILIK = 'P', _('Pemilik')
        ADMIN = 'A', _('Admin')

    role = models.CharField(
        max_length=1,
        choices=Roles.choices,
        default=Roles.ADMIN
    )

    def __str__(self) -> str:
        return f'{self.name} as {self.get_role_display()}'

    class Meta:
        db_table = 'profile'


# log table to store user activity against certain table
# the table tracked are sales, restock, service, sparepart
class Logs(models.Model):
    log_id = models.AutoField(
        primary_key=True,
        unique=True,
    )
    log_at = models.DateTimeField(auto_now_add=True)
    table = models.CharField(max_length=10, default='Sparepart')

    class Operations(models.TextChoices):
        CREATE = 'C', _('Create')
        REMOVE = 'R', _('Remove')
        EDIT = 'E', _('Edit')

    operation = models.CharField(
        max_length=1,
        choices=Operations.choices,
        default=Operations.EDIT
    )
    user_id = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        db_column='user_id',
        null=True
    )

    def __str__(self) -> str:
        return f"at {self.log_at.strftime('%d-%m-%Y %H:%M:%S')} {self.user_id.profile.name} "\
               f"{self.get_operation_display()} a record from {self.table}"\


    class Meta:
        db_table = 'log'


# Customer table to store customer data, purchase and service records
class Customer(models.Model):
    customer_id = models.AutoField(
        primary_key=True,
        unique=True,
    )
    name = models.CharField(max_length=30)
    contact = models.CharField(max_length=15)
    number_of_service = models.PositiveSmallIntegerField(default=0)
    total_payment = models.DecimalField(max_digits=15, decimal_places=0, default=0)

    def __str__(self) -> str:
        return f'{self.name} | Total payment = Rp {self.total_payment}| '\
               f'Total service = {self.number_of_service}'

    class Meta:
        db_table = 'customer'


# abstract base table for transactions
class Base_transaction(models.Model):
    is_paid_off = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pass

    class Meta:
        abstract = True


# sales table to store surface level sales information
class Sales(Base_transaction):
    sales_id = models.BigAutoField(
        primary_key=True,
        unique=True
    )
    deposit = models.DecimalField(max_digits=15, decimal_places=0, default=0)

    user_id = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        db_column='user_id'
    )
    customer_id = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        null=True,
        db_column='customer_id'
    )

    def __str__(self) -> str:
        return f'{self.sales_id} at {self.created_at} | Lunas={self.is_paid_off}'

    class Meta:
        db_table = 'sales'


# sales_detail table store the detail of sales per sparepart
class Sales_detail(models.Model):
    sales_detail_id = models.BigAutoField(
        primary_key=True,
        unique=True
    )
    quantity = models.PositiveSmallIntegerField()
    is_workshop = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    sales_id = models.ForeignKey(
        Sales,
        on_delete=models.CASCADE,
        db_column='sales_id'
    )
    sparepart_id = models.ForeignKey(
        'Sparepart',
        on_delete=models.SET_NULL,
        null=True,
        db_column='supplier_id'
    )

    def __str__(self) -> str:
        return f'{self.sales_id.sales_id}-{self.sales_detail_id}| '\
               f'{self.sparepart_id.name} sold {self.quantity}s qty | '

    class Meta:
        db_table = 'sales_detail'
        constraints = [
            models.UniqueConstraint(
                fields=['sales_id', 'sparepart_id'],
                name='unique_sales_detail',
            )
        ]


# restock table to store surface level information of restock
class Restock(Base_transaction):
    restock_id = models.BigAutoField(
        primary_key=True,
        unique=True,
    )
    no_faktur = models.CharField(max_length=30, default='')
    due_date = models.DateField(null=True)
    deposit = models.DecimalField(max_digits=15, decimal_places=0, default=0)

    user_id = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        db_column='user_id'
    )
    supplier_id = models.ForeignKey(
        'Supplier',
        on_delete=models.SET_NULL,
        null=True,
        db_column='supplier_id'
    )
    salesman_id = models.ForeignKey(
        'Salesman',
        on_delete=models.SET_NULL,
        null=True,
        db_column='salesman_id'
    )

    def __str__(self) -> str:
        return f'{self.restock_id} at {self.created_at} | Lunas={self.is_paid_off}'

    class Meta:
        db_table = 'restock'


# restock_detail table store the detail of restock per sparepart
class Restock_detail(models.Model):
    restock_detail_id = models.BigAutoField(
        primary_key=True,
        unique=True
    )
    quantity = models.PositiveSmallIntegerField()
    individual_price = models.DecimalField(max_digits=15, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)

    restock_id = models.ForeignKey(
        Restock,
        on_delete=models.CASCADE,
        db_column='restock_id'
    )
    sparepart_id = models.ForeignKey(
        'Sparepart',
        null=True,
        on_delete=models.SET_NULL,
        db_column='sparepart_id'
    )

    def __str__(self) -> str:
        return f'{self.restock_id.restock_id}-{self.restock_detail_id}| '\
               f'{self.sparepart_id.name} restock {self.quantity}s qty'

    class Meta:
        db_table = 'restock_detail'
        constraints = [
            models.UniqueConstraint(
                fields=['restock_id', 'sparepart_id'],
                name='unique_restock_detail',
            )
        ]


# Supplier table to store supplier information that supplies workshop with sparepart
class Supplier(models.Model):
    supplier_id = models.AutoField(
        primary_key=True,
        unique=True
    )
    name = models.CharField(max_length=20)
    contact = models.CharField(max_length=13)
    rekening_number = models.CharField(max_length=20, default='')
    rekening_name = models.CharField(max_length=30, default='')
    rekening_bank = models.CharField(max_length=20, default='')

    def __str__(self) -> str:
        return f'{self.name} | {self.contact}'

    class Meta:
        db_table = 'supplier'


# Salesman table to store salesman information, representation from supplier
class Salesman(models.Model):
    salesman_id = models.AutoField(
        primary_key=True,
        unique=True
    )

    name = models.CharField(max_length=20)
    contact = models.CharField(max_length=13)

    supplier_id = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        db_column='supplier_id'
    )

    def __str__(self) -> str:
        return f'{self.name} | {self.contact}'

    class Meta:
        db_table = 'salesman'


# storage table to store sparepart location information
class Storage(models.Model):
    storage_id = models.AutoField(
        primary_key=True,
        unique=True
    )
    code = models.CharField(max_length=8, unique=True)

    class Locations(models.TextChoices):
        FIRST = '1', _('Bengkel 1 Jalan ...')
        SECOND = '2', _('Bengkel 2 Jalan ...')
    location = models.CharField(
        max_length=30,
        choices=Locations.choices,
        default=Locations.FIRST
    )

    is_full = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'Storage {self.location} | full={self.is_full}'

    class Meta:
        db_table = 'storage'


# brand table to store brand name of sparepart
class Brand(models.Model):
    brand_id = models.AutoField(
        primary_key=True,
        unique=True
    )
    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        db_table = 'brand'


# Category table to store category name of sparepart
class Category(models.Model):
    category_id = models.AutoField(
        primary_key=True,
        unique=True
    )
    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        db_table = 'category'


# sparepart table to store information about sparepart
class Sparepart(models.Model):
    def sparepart_image_filename(instance, filename) -> str:
        extension = filename.split('.')[-1]
        filename = str(uuid4())
        return f'images/spareparts/{filename}.{extension}'

    sparepart_id = models.AutoField(
        primary_key=True,
        unique=True
    )
    name = models.CharField(max_length=30, db_index=True)
    partnumber = models.CharField(max_length=20, default='')
    quantity = models.SmallIntegerField()
    limit = models.PositiveSmallIntegerField(default=10)
    motor_type = models.CharField(max_length=20, default='')
    sparepart_type = models.CharField(max_length=20)
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=sparepart_image_filename,
        validators=[validate_image_size]
    )
    price = models.DecimalField(max_digits=15, decimal_places=0)
    workshop_price = models.DecimalField(max_digits=15, decimal_places=0, null=True)
    install_price = models.DecimalField(max_digits=15, decimal_places=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    brand_id = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        db_column='brand_id'
    )
    category_id = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        db_column='category_id'
    )
    storage_id = models.ForeignKey(
        Storage,
        on_delete=models.SET_NULL,
        null=True,
        db_column='storage_id'
    )

    def __str__(self) -> str:
        return f'{self.name} | Rp {self.price} | stock={self.quantity}'

    class Meta:
        db_table = 'sparepart'


# Mechanic table to store workshop's mechanic data
class Mechanic(models.Model):
    mechanic_id = models.AutoField(
        primary_key=True,
        unique=True,
    )
    name = models.CharField(max_length=30)
    contact = models.CharField(max_length=15)
    address = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        db_table = 'mechanic'


# Service table to store surface level information of service
class Service(Base_transaction):
    service_id = models.BigAutoField(
        primary_key=True,
        unique=True,
    )

    police_number = models.CharField(max_length=10)
    motor_type = models.CharField(max_length=20)
    deposit = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=0)

    user_id = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        db_column='user_id'
    )
    mechanic_id = models.ForeignKey(
        Mechanic,
        on_delete=models.SET_NULL,
        null=True,
        db_column='mechanic_id'
    )
    customer_id = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        db_column='customer_id'
    )

    def __str__(self) -> str:
        return f'{self.service_id} | Rp {self.deposit} | Lunas={self.is_paid_off}'

    class Meta:
        db_table = 'service'


# Service action table to store the all action required per service
class Service_action(models.Model):
    service_action_id = models.BigAutoField(
        primary_key=True,
        unique=True,
    )

    name = models.CharField(max_length=30)
    cost = models.DecimalField(max_digits=15, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)

    service_id = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        db_column='service_id'
    )

    def __str__(self) -> str:
        return f'{self.service_id} - Rp {self.service_action_id}| '\
               f'{self.name} - Rp {self.cost}'

    class Meta:
        db_table = 'service_action'


# Service sparepart table to store the usage of sparepart per service
class Service_sparepart(models.Model):
    service_sparepart_id = models.BigAutoField(
        primary_key=True,
        unique=True,
    )
    quantity = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    service_id = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        null=True,
        db_column='service_id'
    )
    sparepart_id = models.ForeignKey(
        Sparepart,
        on_delete=models.SET_NULL,
        null=True,
        db_column='sparepart_id'
    )

    def __str__(self) -> str:
        return f'{self.service_id} - Rp {self.service_sparepart_id}| '\
               f'{self.sparepart_id.name} |  {self.quantity}s qty'

    class Meta:
        db_table = 'service_sparepart'
        constraints = [
            models.UniqueConstraint(
                fields=['service_id', 'sparepart_id'],
                name='unique_service_sparepart',
            )
        ]
