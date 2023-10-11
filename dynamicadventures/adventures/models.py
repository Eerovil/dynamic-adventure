from django.db import models


from .managers import SceneManager

# Create your models here.

import logging
logger = logging.getLogger(__name__)


class Scene(models.Model):
    TIMEOUT_TYPE_ENGINE = 'engine'
    TIMEOUT_TYPE_WEAPON = 'weapon'
    TIMEOUT_TYPE_BUILDING = 'building'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    show_hp = models.BooleanField(default=False)
    sound = models.FileField(upload_to='sounds/', null=True, blank=True)
    timeout = models.IntegerField(null=True, blank=True)
    timeout_type = models.CharField(
        choices=[
            (TIMEOUT_TYPE_ENGINE, 'Engine'),
            (TIMEOUT_TYPE_WEAPON, 'Weapon'),
            (TIMEOUT_TYPE_BUILDING, 'Building'),
        ], max_length=200,
        null=True, blank=True,
        default=TIMEOUT_TYPE_BUILDING,
    )
    timeout_next_scene = models.ForeignKey(
        'Scene', on_delete=models.SET_NULL,
        related_name='timeout_prev_scene', null=True, blank=True
    )

    is_root_scene = models.BooleanField(default=False, null=True)
    is_menu = models.BooleanField(default=False)
    apriltag = models.IntegerField(null=True, blank=True, unique=True)

    objects = SceneManager()

    class Meta:
        ordering = ('is_menu', '-is_root_scene')

    def __str__(self):
        parent_scenes = self.get_all_parent_scenes()
        parents = ' -> '.join([scene.title for scene in parent_scenes])
        if not parents:
            return self.title
        return f"{parents} -> {self.title}"

    def get_all_parent_scenes(self):
        ret = []
        checked_scene_ids = set()
        last_scene = self
        while True:
            try:
                if last_scene.is_root_scene:
                    break
                if last_scene.id in checked_scene_ids:
                    break
                checked_scene_ids.add(last_scene.id)
                new_scene = last_scene.as_btn_next_scene.first().scene
                # prepend to ret
                ret.insert(0, new_scene)
                last_scene = new_scene
            except AttributeError:
                # No parent scene
                break
        return ret

    @property
    def get_url(self):
        if self.slug == 'inventory':
            return '/adventure/inventory/'
        if self.slug == 'ship':
            return '/adventure/ship/'
        if self.slug == 'player':
            return '/adventure/player/'
        return '/adventure/scene/{}/'.format(self.id)

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
        return f"{self.scene}: {self.text}"

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
            user.player.modify_inventory(self.item_add, 1)
        if self.item_remove:
            user.player.modify_inventory(self.item_remove, -1)

    def visible_for_user(self, user):
        questline_row = self.questline_row
        if not questline_row:
            return True
        progress_sort_order = 1
        completed_questline_ids = set()
        for progress in user.player.playerquestprogress_set.all():
            if progress.completed:
                completed_questline_ids.add(progress.quest_row.questline_id)
            if progress.quest_row.questline_id == questline_row.questline_id:
                progress_sort_order = progress.quest_row.sort_order
                if progress.completed:
                    return False

        if questline_row.sort_order > progress_sort_order:
            return False

        if questline_row.show_until and progress_sort_order > questline_row.show_until:
            return False

        for required_questline in questline_row.questline.required_questlines.all():
            if required_questline.id not in completed_questline_ids:
                logger.info("Not showing %s because %s is not completed", self, required_questline)
                return False

        return True


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

    def modify_inventory(self, item, quantity_diff):
        inventory_row, created = self.inventoryrow_set.get_or_create(item=item)
        inventory_row.quantity += quantity_diff
        logger.info("Modifying inventory for %s: %s x %s", self, item, quantity_diff)
        if inventory_row.quantity <= 0:
            inventory_row.delete()
        else:
            inventory_row.save()

    def inventory_as_buttons(self, current_scene):
        ret = []
        for row in self.inventoryrow_set.all():
            button = SceneButton(
                text=f'{row.item} x{row.quantity}',
                image=row.item.image,
                next_scene=current_scene,
                scene=current_scene,
            )
            button.query_params = '?item={}'.format(row.item.id)
            ret.append(button)
        return ret

    def ship_parts_as_buttons(self, current_scene):
        ret = []
        for row in self.inventoryrow_set.all():
            if not row.item.ship_part_type:
                continue
            button = SceneButton(
                text=f'{row.item} x{row.quantity}',
                image=row.item.image,
                next_scene=Scene.objects.get_ship_building_scene(),
                scene=current_scene,
            )
            button.query_params = '?item-built={}'.format(row.item.id)
            ret.append(button)
        return ret

    def build_item(self, item):
        logger.info("Building item %s for %s", item, self)
        if not item.ship_part_type:
            return
        old_item = None
        if item.ship_part_type == 'engine':
            old_item = self.ship_engine_item
            self.ship_engine_item = item
        elif item.ship_part_type == 'shield':
            old_item = self.ship_shield_item
            self.ship_shield_item = item
        elif item.ship_part_type == 'weapon':
            old_item = self.ship_weapon_item
            self.ship_weapon_item = item

        # Remove item from inventory
        self.modify_inventory(item, -1)
        if old_item:
            self.modify_inventory(old_item, 1)
        self.save()

class InventoryRow(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)


class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    quest_item = models.BooleanField(default=False)
    ship_part_type = models.CharField(
        choices=[
            ('engine', 'Engine'),
            ('shield', 'Shield'),
            ('weapon', 'Weapon'),
        ], max_length=200,
        null=True, blank=True,
    )
    ship_part_level = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    @property
    def timeout_effect(self):
        if not self.ship_part_level:
            return 0
        return self.ship_part_level * 2


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
    show_until = models.IntegerField(
        'Näytä kunnes pelaaja on tehnyt kohdan X',
        null=True, blank=True, default=1
    )
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
        progress = PlayerQuestProgress.objects.filter(
            player=user.player, quest_row__questline=self.questline
        ).first()
        if not progress:
            progress = PlayerQuestProgress.objects.create(
                player=user.player, quest_row=self
            )
        if self.sort_order < progress.quest_row.sort_order:
            # Player is ahead of this part of the quest
            return
        progress.quest_row = next_quest_row
        progress.completed = complete
        progress.save()

class QuestLine(models.Model):
    name = models.CharField(max_length=200)
    required_questlines = models.ManyToManyField(
        'self', blank=True,
        help_text='What questlines must be complete to make the questline available?',
        symmetrical=False,
        related_name='as_required_questline_for_questlines',
    )
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
