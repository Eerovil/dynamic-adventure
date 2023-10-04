from django.shortcuts import get_object_or_404, render
from django.views import View

# Create your views here.

from . import models as m


class SceneView(View):
    def get(self, request, scene_id):
        scene = get_object_or_404(m.Scene, pk=scene_id)
        scene_buttons = m.SceneButton.objects.filter(scene=scene)
        context = {
            'scene': scene,
            'scene_buttons': scene_buttons,
        }
        return render(request, 'adventures/scene.html', context)
