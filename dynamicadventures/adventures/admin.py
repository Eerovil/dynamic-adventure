from django.contrib import admin

# Register your models here.

from . import models


class SceneButtonInline(admin.TabularInline):
    fk_name = 'scene'
    model = models.SceneButton
    extra = 1


class SceneAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'image', 'show_hp', 'sound', 'timeout', 'timeout_next_scene')
    inlines = [SceneButtonInline]


admin.site.register(models.Scene, SceneAdmin)
admin.site.register(models.SceneButton)
admin.site.register(models.Player)
admin.site.register(models.InventoryRow)
admin.site.register(models.Item)
admin.site.register(models.QuestLineRow)
admin.site.register(models.QuestLine)
