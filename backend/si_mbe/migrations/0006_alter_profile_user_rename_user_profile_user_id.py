# Generated by Django 4.1.3 on 2022-12-16 15:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('si_mbe', '0005_alter_profile_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='user',
            new_name='user_id',
        ),
    ]
