from django.urls import path
import core.views


app_name = 'core'

urlpatterns = [
    path("", core.views.game),
    path("select/", core.views.select_game, name='select'),
    path('start/<int:game_id>/', core.views.start_game, name='start'),
    path("start/", core.views.start_game, name='start'),
    path('go/<int:game_id>/', core.views.game, name='game'),
    path("go/", core.views.game, name='game'),
    path('complete/<int:game_id>/', core.views.complete_game, name='complete'),
    path("complete/", core.views.complete_game, name='complete'),
]
