# Generated by Django 4.1.5 on 2023-02-01 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_question_columns_alter_question_papers'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='year',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]