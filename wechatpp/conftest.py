import pytest


@pytest.fixture
def user(db):
    """Create and return a test user."""
    from chatapp.tests.factories import UserFactory
    return UserFactory()


@pytest.fixture
def client(db):
    """Return an unauthenticated Django test client."""
    from django.test import Client
    return Client()


@pytest.fixture
def authenticated_client(db, user):
    """Return a Django test client logged in as the test user."""
    from django.test import Client
    c = Client()
    c.login(username=user.username, password="testpass123")
    return c


@pytest.fixture
def room(db):
    """Create and return a test room."""
    from chatapp.tests.factories import RoomFactory
    return RoomFactory()


@pytest.fixture
def message(db, user, room):
    """Create and return a test message associated with the test user and room."""
    from chatapp.tests.factories import MessageFactory
    return MessageFactory(user=user, room=room)


@pytest.fixture
def channel_layer():
    """Return the in-memory channel layer from settings."""
    from channels.layers import get_channel_layer
    return get_channel_layer()
