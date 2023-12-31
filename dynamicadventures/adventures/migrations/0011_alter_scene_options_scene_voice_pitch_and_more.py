# Generated by Django 4.2.5 on 2023-10-11 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventures', '0010_scene_is_root_scene'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scene',
            options={'ordering': ('is_menu', '-is_root_scene')},
        ),
        migrations.AddField(
            model_name='scene',
            name='voice_pitch',
            field=models.FloatField(blank=True, default=1, null=True),
        ),
        migrations.AddField(
            model_name='scene',
            name='voice_rate',
            field=models.FloatField(blank=True, default=1, null=True),
        ),
        migrations.AlterField(
            model_name='questline',
            name='required_questlines',
            field=models.ManyToManyField(blank=True, help_text='What questlines must be complete to make the questline available?', related_name='as_required_questline_for_questlines', to='adventures.questline'),
        ),
    ]
