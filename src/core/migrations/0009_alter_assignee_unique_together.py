# Generated by Django 5.0.6 on 2024-10-24 21:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_alter_user_image'),
        ('core', '0008_alter_board_description_alter_board_name_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='assignee',
            unique_together={('user_id', 'card_id', 'board_id', 'id')},
        ),
    ]
