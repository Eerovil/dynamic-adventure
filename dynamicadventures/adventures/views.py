from django.shortcuts import get_object_or_404, render
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect

# Create your views here.

from . import models as m

import logging
logger = logging.getLogger(__name__)


class SceneView(View):
    template_name = 'adventures/scene.html'

    def extra_context(self):
        return {}

    def scene_buttons_override(self, request, scene):
        return []

    def get(self, request, scene_id):
        if not request.user.is_authenticated:
            return redirect('login_view')
        scene = get_object_or_404(m.Scene, pk=scene_id)
        scene_buttons = self.scene_buttons_override(request, scene)
        if not scene_buttons:
            scene_buttons = [
                btn for btn in
                m.SceneButton.objects.filter(scene=scene)
                if btn.visible_for_user(request.user)
            ]
        scene.handle_quest_progress(request.user)
        scene.handle_button_effects(request.user)
        player = request.user.player
        self.original_scene = player.previous_scene
        # If this class is not SceneView, then do not save previous scene
        if self.__class__ == SceneView:
            player.previous_scene = scene
            player.save()

        if scene.timeout:
            # If scene has timeout, reduce it if its affected by player's items
            if scene.timeout_type == m.Scene.TIMEOUT_TYPE_ENGINE:
                if player.ship_engine_item:
                    scene.timeout -= player.ship_engine_item.timeout_effect
            elif scene.timeout_type == m.Scene.TIMEOUT_TYPE_WEAPON:
                if player.ship_weapon_item:
                    scene.timeout -= player.ship_weapon_item.timeout_effect

        context = {
            'player': player,
            'scene': scene,
            'scene_buttons': scene_buttons,
        }
        context.update(self.extra_context())
        return render(request, self.template_name, context)


class SceneViewWithBack(SceneView):
    def extra_context(self):
        try:
            return {
                'back_scene': self.original_scene.id,
            }
        except AttributeError:
            return {}

class InventoryView(SceneViewWithBack):
    def extra_context(self):
        ret = super().extra_context()
        if self.request.GET.get('item'):
            item = get_object_or_404(m.Item, pk=self.request.GET.get('item'))
            ret['description_override'] = item.description
        return ret

    def get(self, request):
        scene = get_object_or_404(m.Scene, slug='inventory')
        return super().get(request, scene_id=scene.pk)

    def scene_buttons_override(self, request, scene):
        return request.user.player.inventory_as_buttons(scene)


class ShipView(SceneViewWithBack):
    template_name = 'adventures/ship.html'

    def get(self, request):
        scene = get_object_or_404(m.Scene, slug='ship')
        if self.request.GET.get('item-built'):
            item = get_object_or_404(m.Item, pk=self.request.GET.get('item-built'))
            # Player has built an item
            request.user.player.build_item(item)
        return super().get(request, scene_id=scene.pk)

    def scene_buttons_override(self, request, scene):
        return request.user.player.ship_parts_as_buttons(scene)


class PlayerView(SceneViewWithBack):
    template_name = 'adventures/player.html'

    def get(self, request):
        scene = get_object_or_404(m.Scene, slug='player')
        return super().get(request, scene_id=scene.pk)


class LoginView(View):
    def get(self, request):
        # Find wanted username from query string
        # Get or create user with that username
        # Then log in that user (no password needed)
        # Redirect to scene 1
        username = request.GET.get('username')
        if username:
            user, created = User.objects.get_or_create(username=username)
            login(request, user)
            # make sure user has player
            try:
                player = user.player
            except m.Player.DoesNotExist:
                player = m.Player(user=user)
                player.save()
            for scene in m.Scene.objects.all():
                if scene.slug in ['inventory', 'ship', 'player']:
                    continue
                return redirect('scene_view', scene_id=scene.pk)
        return render(request, 'adventures/login.html')
