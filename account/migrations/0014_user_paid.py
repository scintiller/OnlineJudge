# Generated by Django 2.1.7 on 2019-06-19 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_auto_20190618_0920'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]