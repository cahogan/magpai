from openai import OpenAI
import json


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
