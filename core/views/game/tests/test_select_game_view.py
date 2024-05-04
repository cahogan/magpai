import pytest
from core.views.game.tests.setup import authenticated_client
from django.urls import reverse


class TestSelectGameView:
    SELECT_VIEW_NAME = 'select'

    @pytest.mark.django_db
    def test_lets_user_select_game(self, authenticated_client):
        url = reverse(self.SELECT_VIEW_NAME)
        response = authenticated_client.get(url)
        assert response.status_code == 200
