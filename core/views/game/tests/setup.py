import core.models as models
import pytest
from django.test import Client
from django.contrib.auth.models import User


@pytest.fixture
def game():
    GAME_ID = 1
    game = models.Game(
                        id=GAME_ID,
                        current_judge=None,
                        intro = "This is a test game.",
                        name = "Test Game",
                        prize = "improved test coverage",
                        outro = "Hope your tests passed!",
                       )
    game.save()
    yield game


@pytest.fixture
def completed_game():
    GAME_ID = 2
    judge = models.Judge(
                        id=1,
                        name="Test Judge",
                        personality_string="obsessed with test coverage",
                        profile_image=None,
                        )
    judge.save()
    game = models.Game(
                        id=GAME_ID,
                        current_judge=judge,
                        intro = "This is a test game.",
                        name = "Test Game",
                        prize = "improved test coverage",
                        outro = "Hope your tests passed!",
                       )
    game.save()
    question = models.Question(
                                game=game,
                                order=1,
                                clue="What is the best way to test?",
                                answer="write tests",
                              )
    question.save()
    
    User.objects.get_or_create(username='testuser', password='password')
    question_response = models.QuestionResponse(
                                                question=question,
                                                response="write tests",
                                                user=User.objects.first(),
                                                image=None,
                                                is_correct=True,
                                               )
    question_response.save()
    yield game


@pytest.fixture
def judge():
    JUDGE_ID = 1
    judge = models.Judge(
                            id=JUDGE_ID,
                            name = "Test Judge",
                            personality_string = "obsessed with test coverage",
                            profile_image = None,
                        )
    judge.save()
    yield judge


@pytest.fixture
def authenticated_client():
    client = Client()
    user, _ = User.objects.get_or_create(username='testuser', password='password')
    client.force_login(user)
    yield client

@pytest.fixture
def unauthenticated_client():
    client = Client()
    yield client
