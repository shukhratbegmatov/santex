# Generated by Django 4.0.5 on 2022-06-03 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='created_at',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
