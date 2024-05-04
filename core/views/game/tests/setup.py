import pytest
from django.test import Client
from django.contrib.auth.models import User



@pytest.fixture
def authenticated_client():
    client = Client()
    user = User.objects.create_user(username='testuser', password='password')
    client.force_login(user)
    yield client

@pytest.fixture
def unauthenticated_client():
    client = Client()
    yield client
