from django.shortcuts import render, redirect
import core.models as models
from django.contrib.auth.decorators import login_required


def build_post_game_collage(user, game):
    responses = models.QuestionResponse.objects.filter(user=user, question__game=game)
    # make a dictionary of responses by question
    responses_by_question = {}
    for response in responses:
        if response.question in responses_by_question:
            responses_by_question[response.question].append(response)
        else:
            responses_by_question[response.question] = [response]
    context = {
        "game": game,
        "questions": responses_by_question,
    }
    return context


@login_required
def complete_game(request, game_id=None):
    """
    View which shows users a collage of their answers for a completed game.
    - If no valid game ID is provided, the user will be redirected
      to a page where a game can be selected.
    - If the game is not finished, as indicated by a lack of any
      correct responses for the final question (),
      the user will be redirected to the current stage of
      the game.
    """
    try:
        game = models.Game.objects.prefetch_related("question_set").get(id=game_id)
    except models.Game.DoesNotExist:
        return redirect("core:select")
    
    last_question = models.Question.objects.filter(game=game).order_by('-order').first()
    last_question_answered_correctly = models.QuestionResponse.objects.filter(
        question=last_question,
        user=request.user,
        is_correct=True,
    ).exists()
    
    if last_question_answered_correctly:
        context = build_post_game_collage(request.user, game)
        return render(request, "core/complete.html", context)
    else:
        return redirect("core:game", game_id=game_id)
