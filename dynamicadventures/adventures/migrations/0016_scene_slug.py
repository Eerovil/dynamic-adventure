# Generated by Django 4.2.5 on 2023-10-04 19:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('adventures', '0015_player_previous_scene_alter_inventoryrow_quantity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='scene',
            name='slug',
            field=models.SlugField(default=uuid.uuid4, max_length=200),
            preserve_default=False,
        ),
    ]
