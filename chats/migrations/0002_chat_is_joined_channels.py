# Generated by Django 4.0.5 on 2022-06-05 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='is_joined_channels',
            field=models.BooleanField(default=False),
        ),
    ]