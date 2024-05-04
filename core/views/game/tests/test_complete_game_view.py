import pytest
from core.views.game.tests.setup import game, authenticated_client, completed_game
from django.urls import reverse
import core.models as models


class TestCompleteGameView:
    GAME_ID = 1
    JUDGE_ID = 1
    COMPLETE_VIEW_NAME = 'core:complete'
    SELECT_VIEW_NAME = 'core:select'
    GAME_VIEW_NAME = 'core:game'

    @pytest.mark.django_db
    def test_redirects_to_select_game_if_no_game_id(self, authenticated_client):
        url = reverse(self.COMPLETE_VIEW_NAME)
        response = authenticated_client.get(url)
        assert response.status_code == 302
        assert response.url and response.url == reverse(self.SELECT_VIEW_NAME)

    @pytest.mark.django_db
    def test_redirects_to_select_game_if_bad_game_id(self, authenticated_client):
        game_id = "100"
        url = reverse(self.COMPLETE_VIEW_NAME, kwargs={'game_id': game_id})
        response = authenticated_client.get(url)
        assert response.status_code == 302
        assert response.url and response.url == reverse(self.SELECT_VIEW_NAME)

    @pytest.mark.django_db
    def test_redirects_to_current_game_state_if_game_not_completed(self, authenticated_client, completed_game):
        assert completed_game.current_judge is not None
        last_question_in_game = models.Question.objects.filter(game=completed_game).order_by('order').last()
        assert last_question_in_game is not None
        new_last_question = models.Question(
            game=completed_game,
            order=last_question_in_game.order + 1,
            clue="What is the best way to test?",
            answer="write tests",
        )
        new_last_question.save()
        url = reverse(self.COMPLETE_VIEW_NAME, kwargs={'game_id': completed_game.id})
        response = authenticated_client.get(url)
        assert response.status_code == 302
        assert response.url and response.url == reverse(self.GAME_VIEW_NAME, kwargs={'game_id': completed_game.id})

    @pytest.mark.django_db
    def test_shows_user_collage_if_game_completed(self, authenticated_client, completed_game):
        assert completed_game.current_judge is not None
        last_question_in_game = models.Question.objects.filter(game=completed_game).order_by('order').last()
        assert last_question_in_game is not None
        url = reverse(self.COMPLETE_VIEW_NAME, kwargs={'game_id': completed_game.id})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert response.context['game'] == completed_game
