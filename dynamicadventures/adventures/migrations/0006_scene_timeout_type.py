# Generated by Django 4.2.5 on 2023-10-05 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventures', '0005_item_ship_part_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='scene',
            name='timeout_type',
            field=models.CharField(blank=True, choices=[('engine', 'Engine'), ('weapon', 'Weapon')], max_length=200, null=True),
        ),
    ]
