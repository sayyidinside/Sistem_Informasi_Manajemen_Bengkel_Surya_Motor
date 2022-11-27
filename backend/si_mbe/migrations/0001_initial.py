# Generated by Django 4.1.3 on 2022-11-27 14:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('brand_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'brand',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('role_id', models.SmallAutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'role',
            },
        ),
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('total', models.DecimalField(decimal_places=0, max_digits=15)),
                ('is_paid_off', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sales_id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('customer_name', models.CharField(max_length=25)),
                ('sub_total', models.DecimalField(decimal_places=0, max_digits=15)),
                ('discount', models.DecimalField(decimal_places=0, max_digits=15)),
                ('user_id', models.ForeignKey(db_column='user_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sales',
            },
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('storage_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('code', models.CharField(max_length=8)),
                ('location', models.CharField(max_length=20)),
                ('is_full', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'storage',
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('supplier_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=20)),
                ('address', models.CharField(max_length=30)),
                ('contact_number', models.CharField(max_length=13)),
            ],
            options={
                'db_table': 'supplier',
            },
        ),
        migrations.CreateModel(
            name='Sparepart',
            fields=[
                ('sparepart_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(db_index=True, max_length=20)),
                ('quantity', models.PositiveSmallIntegerField()),
                ('type', models.CharField(max_length=10)),
                ('price', models.DecimalField(decimal_places=0, max_digits=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('brand_id', models.ForeignKey(db_column='brand_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='si_mbe.brand')),
                ('storage_id', models.ForeignKey(db_column='storage_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='si_mbe.storage')),
            ],
            options={
                'db_table': 'sparepart',
            },
        ),
        migrations.CreateModel(
            name='Sales_detail',
            fields=[
                ('sales_detail_id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('quantity', models.PositiveSmallIntegerField()),
                ('individual_price', models.DecimalField(decimal_places=0, max_digits=15)),
                ('total_price', models.DecimalField(decimal_places=0, max_digits=15)),
                ('sales_id', models.ForeignKey(db_column='sales_id', on_delete=django.db.models.deletion.CASCADE, to='si_mbe.sales')),
                ('sparepart_id', models.ForeignKey(db_column='supplier_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='si_mbe.sparepart')),
            ],
            options={
                'db_table': 'sales_detail',
            },
        ),
        migrations.CreateModel(
            name='Restock_detail',
            fields=[
                ('restock_detail_id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('quantity', models.PositiveSmallIntegerField()),
                ('individual_price', models.DecimalField(decimal_places=0, max_digits=15)),
                ('total_price', models.DecimalField(decimal_places=0, max_digits=15)),
                ('restock_id', models.ForeignKey(db_column='restock_id', on_delete=django.db.models.deletion.CASCADE, to='si_mbe.sales')),
                ('sparepart_id', models.ForeignKey(db_column='sparepart_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='si_mbe.sparepart')),
            ],
            options={
                'db_table': 'restock_detail',
            },
        ),
        migrations.CreateModel(
            name='restock',
            fields=[
                ('total', models.DecimalField(decimal_places=0, max_digits=15)),
                ('is_paid_off', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('restock_id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('supplier_id', models.ForeignKey(db_column='supplier_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='si_mbe.supplier')),
                ('user_id', models.ForeignKey(db_column='user_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'restock',
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('log_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('log_at', models.DateTimeField()),
                ('table_name', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('operation', models.CharField(choices=[('C', 'Create'), ('R', 'Remove'), ('E', 'Edit')], default='E', max_length=1)),
                ('user_id', models.ForeignKey(db_column='user_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'log',
            },
        ),
        migrations.CreateModel(
            name='Extend_user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_id', models.ForeignKey(db_column='role_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='si_mbe.role')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='sales_detail',
            constraint=models.UniqueConstraint(fields=('sales_id', 'sparepart_id'), name='unique_sales_detail'),
        ),
        migrations.AddConstraint(
            model_name='restock_detail',
            constraint=models.UniqueConstraint(fields=('restock_id', 'sparepart_id'), name='unique_restock_detail'),
        ),
    ]
