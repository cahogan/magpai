from django.shortcuts import render, redirect
import core.models as models
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
import datetime
import base64
from .judge_submission import check_image_matches
from django.http import HttpResponseNotFound


def convert_base64_to_image(base64_string):
    image_format, image_string = base64_string.split(";base64,")
    image_data = base64.b64decode(image_string)
    current_timestamp = datetime.datetime.now().timestamp()
    unique_image_filename = f"{current_timestamp}.{image_format.split('/')[1]}"
    return ContentFile(image_data, name=unique_image_filename)


def save_question_response(question, justification, user, photo, is_correct):
    image_file = convert_base64_to_image(photo)
    question_response = models.QuestionResponse(
        question=question,
        response=justification,
        user=user,
        image=image_file,
        is_correct=is_correct,
    )
    question_response.save()


@login_required
def judge_submission(request, question_id=None):
    try:
        question = models.Question.objects.get(id=question_id)
    except models.Question.DoesNotExist:
        return HttpResponseNotFound("The submission can't be judged without providing a valid game question.")
    else:
        # todo check that game is in progress (has a judge)
        photo = request.POST.get("photo")
        question_id = request.POST.get("question_id")
        question = models.Question.objects.get(id=question_id)
        judge_response = check_image_matches(photo, question.answer, question.game.current_judge)
        is_correct = judge_response["is_match"]
        user_answered = True
        save_question_response(question, judge_response["justification"],
                               request.user, photo, is_correct)
        if is_correct:
            try:
                next_question = models.Question.objects.get(game=question.game, order=question.order + 1)
            except models.Question.DoesNotExist:
                return redirect("core:complete", game_id=question.game.id)
            else:
                question = next_question
                is_correct = None
                user_answered = False
        context = {
            "game": question.game,
            "question": question,
            "answer": user_answered,
            "is_correct": is_correct,
            "justification": judge_response["justification"],
        }
    return render(request, "core/game.html", context)


@login_required
def game(request, game_id=None):
    try:
        game = models.Game.objects.get(id=game_id)
    except models.Game.DoesNotExist:
        return redirect("core:select")
    
    if request.method == "POST":
        question_id = request.POST.get("question_id")
        return judge_submission(request, question_id)
    else:
        if game.current_judge is None:
            return redirect("core:start", game_id=game_id)
        
        latest_answer = models.QuestionResponse.objects.filter(user=request.user, question__game=game) \
                                                   .order_by("-timestamp").first()
        if latest_answer is None:
            current_question = models.Question.objects.filter(game=game).order_by("order").first()
        else:
            if latest_answer.is_correct:
                try:
                    current_question = models.Question.objects.get(game=game, order=latest_answer.question.order + 1).first()
                except models.Question.DoesNotExist:
                    return redirect("core:complete", game_id=game_id)
            else:
                current_question = latest_answer.question
        context = {
            "game": game,
            "question": current_question,
        }
    return render(request, "core/game.html", context)
