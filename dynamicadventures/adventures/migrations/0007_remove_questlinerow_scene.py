# Generated by Django 4.2.5 on 2023-10-04 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adventures', '0006_remove_questlinerow_parent_scene_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questlinerow',
            name='scene',
        ),
    ]
