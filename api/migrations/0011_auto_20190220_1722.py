# Generated by Django 2.1.7 on 2019-02-20 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20190217_1222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food_category',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
