# Generated by Django 2.1.5 on 2019-02-15 05:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20190215_0240'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member_fridge',
            old_name='member',
            new_name='user',
        ),
    ]
