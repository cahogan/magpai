from django.urls import path
import core.views

urlpatterns = [
    path("", core.views.game),
    path("select/", core.views.select_game, name='select'),
    path("start/", core.views.start_game, name='start'),
    path('start/<int:game_id>/', core.views.start_game, name='start'),
]
