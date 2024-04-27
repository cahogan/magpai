from django.shortcuts import render
import core.models as models
import json


def check_image_matches(base64_image, correct_answer):
        return {"is_match": False, "justification":
                "I'm sorry, I forgot how to output JSON and couldn't make a decision based on the provided image."}

def game(request):
    game = models.Game.objects.get(id=1) # for now
    if request.method == "GET":
        questions = models.Question.objects.filter(game=game).order_by("order")
        context = {
            "game": game,
            "question": questions.first(),
        }
    elif request.method == "POST":
        photo = request.POST.get("photo")
        question_id = request.POST.get("question_id")
        question = models.Question.objects.get(id=question_id)
        judge_response = check_image_matches(photo, question.answer)
        is_correct = judge_response["is_match"]
        user_answered = True
        if is_correct:
            try:
                next_question = models.Question.objects.get(game=game, order=question.order + 1)
            except models.Question.DoesNotExist:
                return render(request, "core/complete.html")
            else:
                question = next_question
                is_correct = None
                user_answered = False
        context = {
            "game": game,
            "question": question,
            "answer": user_answered,
            "is_correct": is_correct,
        }
    return render(request, "core/game.html", context)


