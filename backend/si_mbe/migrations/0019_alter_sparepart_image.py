# Generated by Django 4.1.3 on 2022-12-31 19:22

from django.db import migrations, models
import si_mbe.models
import si_mbe.validators


class Migration(migrations.Migration):

    dependencies = [
        ('si_mbe', '0018_alter_sparepart_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparepart',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=si_mbe.models.Sparepart.sparepart_image_filename, validators=[si_mbe.validators.validate_image_size]),
        ),
    ]