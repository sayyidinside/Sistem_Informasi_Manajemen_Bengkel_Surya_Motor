# Generated by Django 4.1.3 on 2022-12-16 18:24

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('si_mbe', '0006_alter_profile_user_rename_user_profile_user_id'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Log',
            new_name='Logs',
        ),
    ]