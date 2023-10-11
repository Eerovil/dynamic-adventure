from django.contrib import admin

# Register your models here.

from . import models


class SceneButtonInline(admin.TabularInline):
    fk_name = 'scene'
    model = models.SceneButton
    extra = 1


class SceneButtonFromInline(admin.TabularInline):
    fk_name = 'next_scene'
    model = models.SceneButton
    extra = 1


class SceneAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'is_menu', 'is_root_scene', 'text', 'image', 'show_hp', 'sound', 'timeout', 'timeout_next_scene'
    )
    inlines = [SceneButtonInline, SceneButtonFromInline]
    search_fields = ['title', 'text']


class QuestLineRowSceneButtonInline(admin.TabularInline):
    fk_name = 'questline_row'
    model = models.SceneButton
    extra = 1


class QuestLineRowInline(admin.TabularInline):
    model = models.QuestLineRow
    extra = 1
    inlines = [QuestLineRowSceneButtonInline]
    autocomplete_fields = ['scene_button']


class QuestLineAdmin(admin.ModelAdmin):
    list_display = ('name', )
    inlines = [QuestLineRowInline]


class InventoryRowInline(admin.TabularInline):
    model = models.InventoryRow
    extra = 0


class PlayerQuestProgressInline(admin.TabularInline):
    model = models.PlayerQuestProgress
    extra = 0


class PlayerAdmin(admin.ModelAdmin):
    inlines = [PlayerQuestProgressInline, InventoryRowInline]


class SceneButtonAdmin(admin.ModelAdmin):
    list_display = [
        'scene',
        'next_scene',
        'text',
        'item_add',
        'item_remove',
    ]
    autocomplete_fields = ['scene', 'next_scene', 'item_add', 'item_remove']
    search_fields = ['text', 'scene__title']


class ItemAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(models.Scene, SceneAdmin)
admin.site.register(models.SceneButton, SceneButtonAdmin)
admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.InventoryRow)
admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.QuestLineRow)
admin.site.register(models.QuestLine, QuestLineAdmin)
admin.site.register(models.PlayerQuestProgress)
admin.site.register(models.ShopInventoryRow)
admin.site.register(models.ShopKeeper)
