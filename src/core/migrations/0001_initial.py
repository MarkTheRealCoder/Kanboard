# Generated by Django 5.1.1 on 2024-10-16 20:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('image', models.ImageField(height_field=100, upload_to='', width_field=100)),
                ('creation_date', models.DateTimeField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.user')),
            ],
        ),
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=7)),
                ('description', models.TextField()),
                ('index', models.IntegerField()),
                ('board_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.board')),
            ],
            options={
                'unique_together': {('id', 'board_id')},
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('color', models.CharField(max_length=7)),
                ('creation_date', models.DateTimeField()),
                ('expiration_date', models.DateTimeField()),
                ('completion_date', models.DateTimeField()),
                ('story_points', models.IntegerField()),
                ('index', models.IntegerField()),
                ('board_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.board')),
                ('column_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.column')),
            ],
            options={
                'unique_together': {('id', 'board_id')},
            },
        ),
        migrations.CreateModel(
            name='Guests',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('board_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.board')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.user')),
            ],
            options={
                'unique_together': {('user_id', 'board_id')},
            },
        ),
    ]
