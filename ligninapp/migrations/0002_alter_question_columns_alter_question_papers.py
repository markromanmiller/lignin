# Generated by Django 4.1.5 on 2023-02-01 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ligninapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='columns',
            field=models.ManyToManyField(blank=True, to='ligninapp.column'),
        ),
        migrations.AlterField(
            model_name='question',
            name='papers',
            field=models.ManyToManyField(blank=True, to='ligninapp.paper'),
        ),
    ]
