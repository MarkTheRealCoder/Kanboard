# Generated by Django 5.0.6 on 2024-10-20 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_alter_user_image_alter_user_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
