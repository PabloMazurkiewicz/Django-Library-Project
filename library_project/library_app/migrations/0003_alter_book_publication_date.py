# Generated by Django 5.1 on 2024-08-20 15:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0002_alter_book_publication_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='publication_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
