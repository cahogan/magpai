from django.shortcuts import render, redirect
import core.models as models
from openai import OpenAI
import json
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
import datetime
import base64


def check_image_matches(base64_image, correct_answer, judge=None):
    client = OpenAI()
    if judge is None:
        judge_name = "a neutral judge"
        judge_personality = "neutral and impartial"
    else:
        judge_name = judge.name
        judge_personality = judge.personality_string
    judge_string = f"""Also, you are {judge_name}, although still excellent at correctly outputting parse-able json.
    You are {judge_personality}.
    Make sure it's clear that you're {judge_name} and your manner of speaking and personality shines through in the justification!"""
    response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {
            "role": "system",
            "content": f"""
            You are a judge in a scavenger hunt game. {judge_string}
            You need to determine if the provided image could be the correct answer, which is: {correct_answer}.
            Do not reveal what the correct answer actually is in your justification! The players need to figure it out themselves.
            Please output your decision only as correctly formatted json, with the schema:
            is_match: bool, justification: string
            """,
        },
        {
        "role": "user",
        "content": [
            {"type": "text", "text": f"Is this image a good answer?"},
            {
            "type": "image_url",
            "image_url": {
                "url": f"{base64_image}",
                "detail": "low",
            },
            },
        ],
        }
    ],
    max_tokens=300,
    )
    output = response.choices[0].message.content
    try:
        json_output = json.loads(output)
    except json.JSONDecodeError:
        return {"is_match": False, "justification":
                "I'm sorry, I forgot how to output JSON and couldn't make a decision based on the provided image."}
    else:
        return json_output


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
def game(request, game_id=None):
    if game_id is not None:
        game = models.Game.objects.get(id=game_id)
    else:
        game = models.Game.objects.get(id=1) # for now

    if request.method == "GET":
        judge = game.current_judge
        if judge is None:
            judges = models.Judge.objects.all()
            context = {
                "game": game,
                "judges": judges,
            }
            return render(request, "core/start.html", context=context)
        latest_answer = models.QuestionResponse.objects.filter(user=request.user, question__game=game) \
                                                   .order_by("-timestamp").first()
        if latest_answer is not None:
            if latest_answer.is_correct:
                try:
                    current_question = models.Question.objects.get(game=game, order=latest_answer.question.order + 1).first()
                except models.Question.DoesNotExist:
                    context = build_post_game_collage(request.user, game)
                    return render(request, "core/complete.html", context=context)
            else:
                current_question = models.Question.objects.filter(game=game, order=latest_answer.question.order).first()
        else:
            current_question = models.Question.objects.filter(game=game).order_by("order").first()

        context = {
            "game": game,
            "question": current_question,
        }
    elif request.method == "POST":
        if request.POST.get("judge"):
            judge_id = request.POST.get("judge")
            judge = models.Judge.objects.get(id=judge_id)
            game.current_judge = judge
            game.save()
            return redirect(f"/game/{game_id}")
        photo = request.POST.get("photo")
        question_id = request.POST.get("question_id")
        question = models.Question.objects.get(id=question_id)
        judge_response = check_image_matches(photo, question.answer, game.current_judge)
        is_correct = judge_response["is_match"]
        user_answered = True
        save_question_response(question, judge_response["justification"],
                               request.user, photo, is_correct)
        if is_correct:
            try:
                next_question = models.Question.objects.get(game=game, order=question.order + 1)
            except models.Question.DoesNotExist:
                context = build_post_game_collage(request.user, game)
                return render(request, "core/complete.html", context)
            else:
                question = next_question
                is_correct = None
                user_answered = False
        context = {
            "game": game,
            "question": question,
            "answer": user_answered,
            "is_correct": is_correct,
            "justification": judge_response["justification"],
        }
    return render(request, "core/game.html", context)


