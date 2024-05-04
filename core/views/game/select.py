from django.shortcuts import render
import core.models as models
from django.contrib.auth.decorators import login_required


@login_required
def select_game(request):
    context = {
        "games": models.Game.objects.all()
    }
    return render(request, "core/select.html", context)
