# Generated by Django 3.0.6 on 2020-05-17 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_0', '0007_auto_20200517_1944'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teamplayermappings',
            name='all_rounder',
        ),
        migrations.RemoveField(
            model_name='teamplayermappings',
            name='batsmen',
        ),
        migrations.RemoveField(
            model_name='teamplayermappings',
            name='bowler',
        ),
        migrations.RemoveField(
            model_name='teamplayermappings',
            name='un_capped',
        ),
        migrations.RemoveField(
            model_name='teamplayermappings',
            name='w_keeper',
        ),
        migrations.AddField(
            model_name='team',
            name='all_rounder',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='batsmen',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='bowler',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='un_capped',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='w_keeper',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='team',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
