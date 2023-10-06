from django.db import models

import logging
logger = logging.getLogger(__name__)


class SceneManager(models.Manager):
    def get_initial_scene(self):
        scene = self.filter(is_menu=False).first()
        if not scene:
            scene = self.get_target_not_found_scene()
        return scene

    def get_inventory_scene(self):
        scene, created = self.get_or_create(slug='inventory')
        scene.is_menu = True
        scene.title = 'Reppu'
        scene.save()
        return scene

    def get_ship_scene(self):
        scene, created = self.get_or_create(slug='ship')
        scene.is_menu = True
        scene.title = 'Alus'
        scene.save()
        return scene

    def get_ship_building_scene(self):
        scene, created = self.get_or_create(slug='ship-building')
        # if created:
        scene.title = 'Rakennetaan alusta'
        scene.is_menu = True
        scene.timeout = 5
        scene.timeout_next_scene = self.get_ship_scene()
        scene.save()
        return scene    

    def get_player_scene(self):
        scene, created = self.get_or_create(slug='player')
        scene.is_menu = True
        scene.title = 'Ukkeli'
        scene.save()
        return scene

    def get_fly_scene(self):
        scene, created = self.get_or_create(slug='fly')
        scene.title = 'Lennä'
        scene.is_menu = True
        scene.save()
        return scene

    def get_target_not_found_scene(self):
        scene, created = self.get_or_create(slug='target_not_found')
        scene.title = 'Määränpäätä ei löytynyt'
        scene.is_menu = False
        scene.text = (
            'Olet ajelehtinut avaruudessa ilman määränpäätä. Löydä jokin määränpää.'
        )
        scene.save()
        return scene

    def get_by_apriltag(self, tag_id):
        scene = self.filter(apriltag=tag_id).first()
        if not scene:
            logger.info("Apriltag %s not found", tag_id)
            scene = self.get_target_not_found_scene()
        return scene
