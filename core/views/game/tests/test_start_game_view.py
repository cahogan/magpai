import pytest
from django.urls import reverse
from core.views.game.tests.setup import game, judge, authenticated_client
import core.models as models


class TestStartGameView:
    GAME_ID = 1
    JUDGE_ID = 1
    START_VIEW_NAME = 'core:start'
    SELECT_VIEW_NAME = 'core:select'
    GAME_VIEW_NAME = 'core:game'

    @pytest.mark.django_db
    def test_redirects_to_select_game_if_no_game_id(self, authenticated_client):
        url = reverse(self.START_VIEW_NAME)
        response = authenticated_client.get(url)
        assert response.status_code == 302
        assert response.url and response.url == reverse(self.SELECT_VIEW_NAME)

    @pytest.mark.django_db
    def test_redirects_to_select_game_if_bad_game_id(self, authenticated_client):
        game_id = "100"
        url = reverse(self.START_VIEW_NAME, kwargs={'game_id': game_id})
        response = authenticated_client.get(url)
        assert response.status_code == 302
        assert response.url and response.url == reverse(self.SELECT_VIEW_NAME)

    @pytest.mark.django_db
    def test_redirects_to_current_game_state_if_game_started(self, authenticated_client, game, judge):
        assert game.current_judge is None
        game.current_judge = judge
        game.save()
        url = reverse(self.START_VIEW_NAME, kwargs={'game_id': game.id})
        response = authenticated_client.get(url)
        assert response.status_code == 302
        assert response.url and response.url == reverse(self.GAME_VIEW_NAME, kwargs={'game_id': game.id})

    @pytest.mark.django_db
    def test_lets_user_select_judge_if_game_not_started(self, authenticated_client, game):
        assert models.Game.objects.all().count() == 1
        game = models.Game.objects.first()
        assert game.current_judge is None
        url = reverse(self.START_VIEW_NAME, kwargs={'game_id': game.id})
        response = authenticated_client.get(url)
        assert response.status_code == 200
