# Generated by Django 5.1.1 on 2024-10-16 20:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('board_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.board')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.user')),
            ],
            options={
                'unique_together': {('user_id', 'board_id')},
            },
        ),
        migrations.DeleteModel(
            name='Guests',
        ),
    ]
