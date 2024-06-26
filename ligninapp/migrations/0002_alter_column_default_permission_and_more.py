# Generated by Django 4.1.5 on 2024-03-20 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ligninapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='default_permission',
            field=models.CharField(choices=[('NONE', 'None'), ('VIEW', 'View'), ('PROP', 'Propose'), ('MOD', 'Moderate'), ('ADMIN', 'Administrate')], default='MOD', max_length=5),
        ),
        migrations.AlterField(
            model_name='review',
            name='question_text',
            field=models.CharField(help_text='The title of the review', max_length=200),
        ),
    ]
