# Generated by Django 4.2.4 on 2023-08-20 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0003_vehicle'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='description',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vehicle',
            name='url_name',
            field=models.CharField(default=' ', max_length=50),
            preserve_default=False,
        ),
    ]
