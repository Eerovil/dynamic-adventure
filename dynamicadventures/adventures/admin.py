from django.contrib import admin

# Register your models here.

from . import models


class SceneButtonInline(admin.TabularInline):
    fk_name = 'scene'
    model = models.SceneButton
    extra = 1


class SceneAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'is_menu', 'text', 'image', 'show_hp', 'sound', 'timeout', 'timeout_next_scene'
    )
    inlines = [SceneButtonInline]


class QuestLineRowSceneButtonInline(admin.TabularInline):
    fk_name = 'questline_row'
    model = models.SceneButton
    extra = 1


class QuestLineRowInline(admin.TabularInline):
    model = models.QuestLineRow
    extra = 1
    inlines = [QuestLineRowSceneButtonInline]


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


admin.site.register(models.Scene, SceneAdmin)
admin.site.register(models.SceneButton)
admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.InventoryRow)
admin.site.register(models.Item)
admin.site.register(models.QuestLineRow)
admin.site.register(models.QuestLine, QuestLineAdmin)
admin.site.register(models.PlayerQuestProgress)
admin.site.register(models.ShopInventoryRow)
admin.site.register(models.ShopKeeper)
