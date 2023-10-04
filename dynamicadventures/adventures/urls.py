from django.contrib import admin
from django.urls import path, include

from . import views


urlpatterns = [
    path('scene/<int:scene_id>/', views.SceneView.as_view(), name='scene_view'),
    path('', views.LoginView.as_view(), name='login_view'),
    path('inventory/', views.InventoryView.as_view(), name='inventory_view'),
    path('ship/', views.ShipView.as_view(), name='ship_view'),
    path('player/', views.PlayerView.as_view(), name='player_view'),
]
