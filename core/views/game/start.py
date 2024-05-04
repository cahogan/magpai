from django.shortcuts import render, redirect
import core.models as models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseBadRequest


@login_required
def choose_judge(request, game_id):
    try:
        game = models.Game.objects.get(id=game_id)
    except models.Game.DoesNotExist:
        return redirect("core:select")
    
    try: 
        judge_id = request.POST.get("judge")
        judge = models.Judge.objects.get(id=judge_id)
    except ValueError: # check that this is actually the exception for bad request
        return HttpResponseBadRequest("Please include a 'judge' field.")
    except models.Judge.DoesNotExist:
        return HttpResponseNotFound("No judge with the provided ID exists.")
    
    else:
        game.current_judge = judge
        game.save()

    return redirect("core:game", game_id=game_id)


@login_required
def start_game(request, game_id=None):
    """
    View which allows users to start a new game by selecting
    a judge for the game.
    - If no valid game ID is provided, the user will be redirected
      to a page where a game can be selected.
    - If the game has already started, as indicated by the
      presence of a judge (the game.current_judge field),
      the user will be redirected to the current stage of
      the game.
    """
    if request.POST:
        return choose_judge(request, game_id)
    try:
        game = models.Game.objects.get(id=game_id)
    except models.Game.DoesNotExist:
        return redirect("core:select")

    if game.current_judge:
        return redirect("core:game", game_id=game_id)

    judges = models.Judge.objects.all()
    context = {
        "game": game,
        "judges": judges,
    }
    return render(request, "core/start.html", context=context)
