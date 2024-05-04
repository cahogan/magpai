from django.urls import path
import core.views

urlpatterns = [
    path("", core.views.game),
    path("select/", core.views.select_game, name='select'),
]
