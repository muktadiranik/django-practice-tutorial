# Generated by Django 3.2 on 2022-07-27 21:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0007_auto_20220728_0251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
