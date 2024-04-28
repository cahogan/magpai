from django.shortcuts import render
import core.models as models
from openai import OpenAI
import json
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
import datetime
import base64


def check_image_matches(base64_image, correct_answer):
    client = OpenAI()
    judge_string = """Also, you are Gordon Ramsay, although still excellent at correctly outputting parse-able json.
    Make sure it's clear that you're Gordon Ramsay and your manner of speaking and personality shines through in the justification!"""
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


@login_required
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
        save_question_response(question, judge_response["justification"],
                               request.user, photo, is_correct)
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
            "justification": judge_response["justification"],
        }
    return render(request, "core/game.html", context)


