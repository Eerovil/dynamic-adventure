# Generated by Django 4.2.5 on 2023-10-05 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventures', '0007_alter_scene_timeout_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='scene',
            name='apriltag',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
