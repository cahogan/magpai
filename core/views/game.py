from django.shortcuts import render
import core.models as models
from openai import OpenAI
import json


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
            "justification": judge_response["justification"],
        }
    return render(request, "core/game.html", context)


