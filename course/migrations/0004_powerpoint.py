# Generated by Django 2.1.7 on 2019-06-16 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_auto_20190612_1452'),
    ]

    operations = [
        migrations.CreateModel(
            name='PowerPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ppt', models.FileField(upload_to='')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ppt', to='course.Course')),
            ],
        ),
    ]
