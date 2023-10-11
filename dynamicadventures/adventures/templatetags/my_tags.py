

# Templatetags

from django import template

register = template.Library()

# Add a tag that returns all scene objects
@register.simple_tag
def get_menu_scenes():
    """
    usage: {% get_menu_scenes as menu_scenes %}
    """
    from adventures.models import Scene
    return {
        scene.slug: scene for scene in Scene.objects.filter(is_menu=True)
    }
