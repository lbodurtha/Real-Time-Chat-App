import pytest
from django.test import Client
from channels.layers import get_channel_layer

from chatapp.tests.factories import UserFactory, RoomFactory, MessageFactory


@pytest.fixture
def user(db):
    """Create and return a test user."""
    return UserFactory()


@pytest.fixture
def client(db):
    """Return an unauthenticated Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(db, user):
    """Return a Django test client logged in as the test user."""
    c = Client()
    c.login(username=user.username, password="testpass123")
    return c


@pytest.fixture
def room(db):
    """Create and return a test room."""
    return RoomFactory()


@pytest.fixture
def channel_layer():
    """Return the in-memory channel layer from settings."""
    return get_channel_layer()
