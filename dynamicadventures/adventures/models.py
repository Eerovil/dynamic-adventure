from django.db import models

# Create your models here.


class Scene(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    show_hp = models.BooleanField(default=False)
    sound = models.FileField(upload_to='sounds/', null=True, blank=True)
    timeout = models.IntegerField(null=True, blank=True)
    timeout_next_scene = models.ForeignKey(
        'Scene', on_delete=models.CASCADE,
        related_name='timeout_prev_scene', null=True, blank=True
    )

    def __str__(self):
        return self.title


class SceneButton(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    next_scene = models.ForeignKey(
        Scene, on_delete=models.CASCADE, related_name='next_scene', null=True, blank=True
    )
    hp_change = models.IntegerField(null=True, blank=True)
    item_add = models.ForeignKey('Item', on_delete=models.CASCADE, null=True, blank=True)
    item_remove = models.ForeignKey(
        'Item', on_delete=models.CASCADE,
        related_name='scene_button_remove', null=True, blank=True
    )
    image = models.ImageField(upload_to='images/', null=True, blank=True)


class ShopKeeper(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    parent_scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    scene_button = models.ForeignKey(
        SceneButton, on_delete=models.CASCADE,
        related_name='shop_scene_button', null=True, blank=True,
        help_text='SceneButton to add to parent_scene which will show "scene"',
    )


class ShopInventoryRow(models.Model):
    shop = models.ForeignKey(ShopKeeper, on_delete=models.CASCADE)
    item = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)


class Player(models.Model):
    ship_health = models.IntegerField(default=100)
    ship_engine_item = models.ForeignKey(
        'Item', on_delete=models.CASCADE, null=True, blank=True,
        related_name='ship_engine_item'
    )
    ship_shield_item = models.ForeignKey(
        'Item', on_delete=models.CASCADE, null=True, blank=True,
        related_name='ship_shield_item'
    )
    ship_weapon_item = models.ForeignKey(
        'Item', on_delete=models.CASCADE, null=True, blank=True,
        related_name='ship_weapon_item'
    )
    player_hat_item = models.ForeignKey(
        'Item', on_delete=models.CASCADE, null=True, blank=True,
        related_name='player_hat_item'
    )
    player_shirt_item = models.ForeignKey(
        'Item', on_delete=models.CASCADE, null=True, blank=True,
        related_name='player_shirt_item'
    )


class InventoryRow(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    item = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)


class Item(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)


class PlayerQuestProgress(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    quest_row = models.ForeignKey(
        'QuestLineRow', on_delete=models.CASCADE
    )


class QuestLineRow(models.Model):
    sort_order = models.IntegerField(default=1)
    questline = models.ForeignKey('QuestLine', on_delete=models.CASCADE)
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    parent_scene = models.ForeignKey(
        Scene, on_delete=models.CASCADE,
        related_name='parent_scene_for_quest', null=True, blank=True
    )
    scene_button = models.ForeignKey(
        SceneButton, on_delete=models.CASCADE,
        related_name='scene_button_for_quest', null=True, blank=True,
        help_text='SceneButton to add to parent_scene which will show "scene"',
    )

    class Meta:
        ordering = ['sort_order']


class QuestLine(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    required_questlines = models.ManyToManyField(
        'self', blank=True,
        help_text='What questlines must be complete to make the questline available?',
    )
    description = models.TextField()
