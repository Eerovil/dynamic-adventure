# Generated by Django 4.2.5 on 2023-10-05 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventures', '0004_item_ship_part_type_scene_is_menu'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='ship_part_level',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
