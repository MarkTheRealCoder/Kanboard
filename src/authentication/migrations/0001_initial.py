# Generated by Django 5.1.1 on 2024-10-16 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=16, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=32)),
                ('image', models.ImageField(upload_to='')),
                ('name', models.CharField(max_length=32)),
                ('surname', models.CharField(max_length=32)),
                ('last_login', models.DateTimeField()),
                ('date_joined', models.DateTimeField()),
            ],
        ),
    ]
