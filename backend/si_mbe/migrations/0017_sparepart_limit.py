# Generated by Django 4.1.3 on 2022-12-30 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('si_mbe', '0016_alter_restock_detail_restock_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='sparepart',
            name='limit',
            field=models.PositiveSmallIntegerField(default=10),
        ),
    ]