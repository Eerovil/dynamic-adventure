from django.db import models

# Create your models here.

import logging
logger = logging.getLogger(__name__)


class Scene(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    show_hp = models.BooleanField(default=False)
    sound = models.FileField(upload_to='sounds/', null=True, blank=True)
    timeout = models.IntegerField(null=True, blank=True)
    timeout_next_scene = models.ForeignKey(
        'Scene', on_delete=models.SET_NULL,
        related_name='timeout_prev_scene', null=True, blank=True
    )

    def __str__(self):
        return self.title

    @property
    def questline_row(self):
        try:
            return self.as_btn_next_scene.first().questline_row
        except AttributeError:
            # No questline
            pass

    def handle_quest_progress(self, user):
        questline_row = self.questline_row
        if not questline_row:
            return
        questline_row.mark_as_complete(user)

    def handle_button_effects(self, user):
        if not user.player.previous_scene:
            return
        for btn in self.as_btn_next_scene.all():
            if btn.scene == user.player.previous_scene:
                btn.handle_side_effects(user)


class SceneButton(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    next_scene = models.ForeignKey(
        Scene, on_delete=models.SET_NULL, related_name='as_btn_next_scene', null=True, blank=True
    )
    hp_change = models.IntegerField(null=True, blank=True)
    item_add = models.ForeignKey(
        'Item', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='scene_button_add'
    )
    item_remove = models.ForeignKey(
        'Item', on_delete=models.SET_NULL,
        related_name='scene_button_remove', null=True, blank=True
    )
    image = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        return f"{self.scene.title} - {self.text}"

    @property
    def questline_row(self):
        quest_rows = list(self.scene_button_for_quest.all())
        if len(quest_rows) == 0:
            return None
        return quest_rows[0]

    def handle_side_effects(self, user):
        if self.hp_change:
            user.player.ship_health += self.hp_change
            user.player.save()
        if self.item_add:
            inventory_row, created = user.player.inventoryrow_set.get_or_create(item=self.item_add)
            inventory_row.quantity += 1
            inventory_row.save()
        if self.item_remove:
            inventory_row, created = user.player.inventoryrow_set.get_or_create(item=self.item_remove)
            inventory_row.quantity -= 1
            if inventory_row.quantity <= 0:
                inventory_row.delete()
            else:
                inventory_row.save()

    def visible_for_user(self, user):
        questline_row = self.questline_row
        if not questline_row:
            return True
        progress_exists = False
        for progress in user.player.playerquestprogress_set.all():
            if progress.quest_row.questline_id == questline_row.questline_id:
                progress_exists = True
                if progress.completed:
                    return False
            if progress.quest_row_id == questline_row.id:
                return True

        if not progress_exists and questline_row.sort_order == 1:
            # This is the first quest in the questline
            return True
        logger.info("User %s does not have access to scene button %s", user, self)
        return False


class ShopKeeper(models.Model):
    scene = models.ForeignKey(
        Scene, on_delete=models.SET_NULL,
        related_name='shop_scene', null=True, blank=True
    )
    parent_scene = models.ForeignKey(
        Scene, on_delete=models.SET_NULL,
        related_name='parent_scene_for_shop', null=True, blank=True
    )
    scene_button = models.ForeignKey(
        SceneButton, on_delete=models.SET_NULL,
        related_name='shop_scene_button', null=True, blank=True,
        help_text='SceneButton to add to parent_scene which will show "scene"',
    )


class ShopInventoryRow(models.Model):
    shop = models.ForeignKey(ShopKeeper, on_delete=models.CASCADE)
    item = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)


class Player(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='player')
    previous_scene = models.ForeignKey(
        Scene, on_delete=models.SET_NULL,
        related_name='previous_scene_for_player', null=True, blank=True
    )
    ship_health = models.IntegerField(default=100)
    ship_engine_item = models.ForeignKey(
        'Item', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ship_engine_item'
    )
    ship_shield_item = models.ForeignKey(
        'Item', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ship_shield_item'
    )
    ship_weapon_item = models.ForeignKey(
        'Item', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ship_weapon_item'
    )
    player_hat_item = models.ForeignKey(
        'Item', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='player_hat_item'
    )
    player_shirt_item = models.ForeignKey(
        'Item', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='player_shirt_item'
    )

    def __str__(self):
        return self.user.username

    def inventory_as_buttons(self, current_scene):
        ret = []
        for row in self.inventoryrow_set.all():
            button = SceneButton(
                text=f'{row.item} x{row.quantity}',
                image=row.item.image,
                next_scene=current_scene,
                scene=current_scene,
            )
            button.next_scene_url = '/adventure/inventory/?item={}'.format(row.item.id)
            ret.append(button)
        return ret


class InventoryRow(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)


class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    quest_item = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class PlayerQuestProgress(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    quest_row = models.ForeignKey(
        'QuestLineRow', on_delete=models.CASCADE
    )
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.player} - {self.quest_row}'


class QuestLineRow(models.Model):
    sort_order = models.IntegerField(default=1)
    questline = models.ForeignKey('QuestLine', on_delete=models.CASCADE)
    scene_button = models.ForeignKey(
        SceneButton, on_delete=models.SET_NULL,
        related_name='scene_button_for_quest', null=True, blank=True,
        help_text='SceneButton to add to parent scene which will show "scene"',
    )

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        if not self.scene_button:
            return f'{self.questline.name} - No scene button'
        return f'{self.sort_order}: {self.questline.name} - {self.scene_button.text}'

    def save(self, *args, **kwargs):
        siblings = self.questline.questlinerow_set.all()
        if self.id:
            siblings = siblings.exclude(id=self.id)
        if not self.sort_order or siblings.filter(sort_order=self.sort_order).exists():
            max_sort_order = siblings.aggregate(models.Max('sort_order'))['sort_order__max']
            self.sort_order = max_sort_order + 1
        super().save(*args, **kwargs)

    def mark_as_complete(self, user):
        next_quest_row = self.questline.questlinerow_set.filter(sort_order=self.sort_order + 1).first()
        complete = False
        if not next_quest_row:
            next_quest_row = self
            complete = True
        progress = PlayerQuestProgress.objects.get_or_create(player=user.player, quest_row=self)[0]
        progress.quest_row = next_quest_row
        progress.completed = complete
        progress.save()

class QuestLine(models.Model):
    name = models.CharField(max_length=200)
    required_questlines = models.ManyToManyField(
        'self', blank=True,
        help_text='What questlines must be complete to make the questline available?',
    )
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
