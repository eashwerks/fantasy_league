# Generated by Django 3.0.6 on 2020-05-17 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_0', '0006_auto_20200517_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teamplayermappings',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
