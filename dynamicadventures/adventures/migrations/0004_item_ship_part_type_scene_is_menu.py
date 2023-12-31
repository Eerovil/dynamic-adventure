# Generated by Django 4.2.5 on 2023-10-05 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventures', '0003_alter_scene_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='ship_part_type',
            field=models.CharField(blank=True, choices=[('engine', 'Engine'), ('shield', 'Shield'), ('weapon', 'Weapon')], max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='scene',
            name='is_menu',
            field=models.BooleanField(default=False),
        ),
    ]
