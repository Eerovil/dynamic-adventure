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
    def get(self, request, scene_id):
        if not request.user.is_authenticated:
            return redirect('login_view')
        scene = get_object_or_404(m.Scene, pk=scene_id)
        scene_buttons = [
            btn for btn in
            m.SceneButton.objects.filter(scene=scene)
            if btn.visible_for_user(request.user)
        ]
        scene.handle_quest_progress(request.user)

        context = {
            'scene': scene,
            'scene_buttons': scene_buttons,
        }
        return render(request, 'adventures/scene.html', context)


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
            return redirect('scene_view', scene_id=1)
        return render(request, 'adventures/login.html')
