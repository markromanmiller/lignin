# Generated by Django 4.1.5 on 2024-03-19 16:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ligninapp', '0003_remove_column_creator_column_default_permission_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='default_subpaper',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='default_of', to='ligninapp.subpaper'),
        ),
        migrations.AlterField(
            model_name='subpaper',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
