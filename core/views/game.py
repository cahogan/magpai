from django.shortcuts import render
import core.models as models

def game(request):
    game = models.Game.objects.get(id=1) # for now
    questions = models.Question.objects.filter(game=game).order_by("order")
    context = {
        "game": game,
        "questions": questions,
    }
    return render(request, "core/game.html", context)


