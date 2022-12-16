from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.


# role tabel to categorize user to different role and permission
# consist of role_id as pk, name as role name
class Role(models.Model):
    role_id = models.SmallAutoField(
        primary_key=True,
        unique=True,
    )
    name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        db_table = 'role'


# Profile tabel is extended of user tabel to give each user their perpective informations
class Profile(models.Model):
    user_id = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    name = models.CharField(max_length=30, default='')
    contact_number = models.CharField(max_length=13, default='')
    role_id = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        db_column='role_id'
    )

    def __str__(self) -> str:
        return f'{self.user.username} as {self.role_id.name}'

    class Meta:
        db_table = 'profile'


# log table to store user activity against certain table
# the table tracked are sales, sales_detail, restock, restock_detail, sparepart
# log table consist of log_id as pk, log_at, log_at (time), table_name, user_id
class Log(models.Model):
    log_id = models.AutoField(
        primary_key=True,
        unique=True,
    )
    log_at = models.DateTimeField(auto_now_add=True)
    table_name = models.CharField(max_length=20)

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
        null=True,
        db_column='user_id'
    )

    def __str__(self) -> str:
        return f'at {self.log_at} {self.user_id} {self.user_id} a record from {self.table_name}'

    class Meta:
        db_table = 'log'


# abstract base table for transactions
class Base_transaction(models.Model):
    is_paid_off = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pass

    class Meta:
        abstract = True


# sales table to store surface level sales information
# consist of sales_id as pk, customer_name, sub_total, discount, user_id,
# total, is_paid_off, created_at, updated_at
class Sales(Base_transaction):
    sales_id = models.BigAutoField(
        primary_key=True,
        unique=True
    )
    customer_name = models.CharField(max_length=25, blank=True)
    customer_contact = models.CharField(max_length=13, blank=True)
    user_id = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        db_column='user_id'
    )

    def __str__(self) -> str:
        return f'{self.sales_id} at {self.created_at} | Lunas={self.is_paid_off}'

    class Meta:
        db_table = 'sales'


# sales_detail table store the detail of sales per sparepart
# consist of sales_detail_id as pk, quantity, individual_price, total_price
# sales_id
class Sales_detail(models.Model):
    sales_detail_id = models.BigAutoField(
        primary_key=True,
        unique=True
    )
    quantity = models.PositiveSmallIntegerField()
    is_grosir = models.BooleanField(default=False)
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
               f'{self.sparepart_id.name} sold {self.quantity}s qty | '\
               f'grosir={self.is_grosir}'

    class Meta:
        db_table = 'sales_detail'
        constraints = [
            models.UniqueConstraint(
                fields=['sales_id', 'sparepart_id'],
                name='unique_sales_detail',
            )
        ]


# restock table to store surface level information of restock
# consist of restock_id as pk, user_id, supplier_id
class Restock(Base_transaction):
    restock_id = models.BigAutoField(
        primary_key=True,
        unique=True,
    )
    no_faktur = models.CharField(max_length=30, default='')
    due_date = models.DateField(null=True)
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

    def __str__(self) -> str:
        return f'{self.restock_id} at {self.created_at} | Lunas={self.is_paid_off}'

    class Meta:
        db_table = 'restock'


# restock_detail table store the detail of restock per sparepart
# consist of restock_detail_id as pk, quantity, individual_price, total_price,
# restock_id, sparepart_id
class Restock_detail(models.Model):
    restock_detail_id = models.BigAutoField(
        primary_key=True,
        unique=True
    )
    quantity = models.PositiveSmallIntegerField()
    individual_price = models.DecimalField(max_digits=15, decimal_places=0)
    restock_id = models.ForeignKey(
        Restock,
        on_delete=models.CASCADE,
        db_column='restock_id'
    )
    sparepart_id = models.ForeignKey(
        'Sparepart',
        on_delete=models.SET_NULL,
        null=True,
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


# Supplier table to store supplier information that supplies us sparepart
# consist of supplier_id as pk, name, address, contact_number
class Supplier(models.Model):
    supplier_id = models.AutoField(
        primary_key=True,
        unique=True
    )
    name = models.CharField(max_length=20)
    address = models.CharField(max_length=30)
    contact_number = models.CharField(max_length=13)
    salesman_name = models.CharField(max_length=30, blank=True)
    salesman_contact = models.CharField(max_length=13, blank=True)

    def __str__(self) -> str:
        return f'{self.name} | {self.contact_number}'

    class Meta:
        db_table = 'supplier'


# storage table to store sparepart location information
# consist of storage_id as pk, code, location, is_full
class Storage(models.Model):
    storage_id = models.AutoField(
        primary_key=True,
        unique=True
    )
    code = models.CharField(max_length=8)
    location = models.CharField(max_length=20)
    is_full = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'Storage {self.location} | full={self.is_full}'

    class Meta:
        db_table = 'storage'


# brand table to store brand name of sparepart
# consist of brand_id as pk, name
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


# sparepart table to store information about sparepart
# consist of sparepart_id as pk, name, quantity, type, price, created_at,
# updated_at, brand_id, storage_id
class Sparepart(models.Model):
    sparepart_id = models.AutoField(
        primary_key=True,
        unique=True
    )
    name = models.CharField(max_length=20, db_index=True)
    partnumber = models.CharField(max_length=20, default='')
    quantity = models.PositiveSmallIntegerField()
    motor_type = models.CharField(max_length=20, default='')
    sparepart_type = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=15, decimal_places=0)
    grosir_price = models.DecimalField(max_digits=15, decimal_places=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    brand_id = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        db_column='brand_id'
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
