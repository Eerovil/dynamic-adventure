from django.db import models


class SceneManager(models.Manager):
    def get_inventory_scene(self):
        scene, created = self.get_or_create(slug='inventory')
        scene.is_menu = True
        scene.title = 'Inventory'
        scene.save()
        return scene

    def get_ship_scene(self):
        scene, created = self.get_or_create(slug='ship')
        scene.is_menu = True
        scene.title = 'Ship'
        scene.save()
        return scene

    def get_ship_building_scene(self):
        scene, created = self.get_or_create(slug='ship-building')
        # if created:
        scene.title = 'Ship Building'
        scene.is_menu = True
        scene.timeout = 5
        scene.timeout_next_scene = self.get_ship_scene()
        scene.save()
        return scene

    def get_player_scene(self):
        scene, created = self.get_or_create(slug='player')
        scene.is_menu = True
        scene.title = 'Player'
        scene.save()
        return scene
