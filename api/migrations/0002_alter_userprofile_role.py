# Generated by Django 5.1 on 2024-08-19 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('Manager', 'Manager'), ('Customer', 'Customer')], default='Customer', max_length=20),
        ),
    ]
