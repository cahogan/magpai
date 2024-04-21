from django.shortcuts import render
import core.models as models

def game(request):
    game = models.Game.objects.get(id=1) # for now
    if request.method == "GET":
        questions = models.Question.objects.filter(game=game).order_by("order")
        context = {
            "game": game,
            "question": questions.first(),
        }
    elif request.method == "POST":
        question_id = request.POST.get("question_id")
        answer = request.POST.get("answer")
        question = models.Question.objects.get(id=question_id)
        is_correct = (answer == question.answer)
        if is_correct:
            try:
                next_question = models.Question.objects.get(game=game, order=question.order + 1)
            except models.Question.DoesNotExist:
                return render(request, "core/complete.html")
            else:
                question = next_question
                is_correct = None
                answer = None
        context = {
            "game": game,
            "question": question,
            "answer": answer,
            "is_correct": is_correct,
        }
    return render(request, "core/game.html", context)


