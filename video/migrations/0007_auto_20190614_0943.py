# Generated by Django 2.1.7 on 2019-06-14 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0006_auto_20190614_0923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solutionvideo',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solution_video', to='problem.Problem'),
        ),
    ]
