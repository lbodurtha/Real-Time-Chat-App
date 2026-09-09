import pytest
from django.urls import reverse

from chatapp.models import Room, Message
from chatapp.tests.factories import UserFactory, RoomFactory, MessageFactory


@pytest.mark.django_db
class TestRoomsView:
    """Tests for the rooms() view."""

    def test_rooms_view_returns_200_authenticated(self, authenticated_client):
        """Test rooms view returns HTTP 200 for an authenticated user."""
        response = authenticated_client.get(reverse("rooms"))
        assert response.status_code == 200

    def test_rooms_view_uses_correct_template(self, authenticated_client):
        """Test rooms view renders the 'rooms.html' template."""
        response = authenticated_client.get(reverse("rooms"))
        assert "rooms.html" in [t.name for t in response.templates]

    def test_rooms_view_context_contains_rooms(self, authenticated_client):
        """Test rooms view passes all Room objects in context."""
        room1 = RoomFactory(name="Room A", slug="room-a")
        room2 = RoomFactory(name="Room B", slug="room-b")
        response = authenticated_client.get(reverse("rooms"))
        rooms_in_context = list(response.context["rooms"])
        assert room1 in rooms_in_context
        assert room2 in rooms_in_context
        assert len(rooms_in_context) == 2

    def test_rooms_view_empty_rooms(self, authenticated_client):
        """Test rooms view with no rooms in database."""
        response = authenticated_client.get(reverse("rooms"))
        rooms_in_context = list(response.context["rooms"])
        assert len(rooms_in_context) == 0

    def test_rooms_view_unauthenticated_returns_200(self, client):
        """Test unauthenticated user can still access rooms view (returns 200)."""
        response = client.get(reverse("rooms"))
        assert response.status_code == 200

    def test_rooms_view_unauthenticated_shows_not_logged_in(self, client):
        """Test unauthenticated user sees 'not logged in' content."""
        response = client.get(reverse("rooms"))
        content = response.content.decode()
        assert "You are not logged in" in content


@pytest.mark.django_db
class TestRoomView:
    """Tests for the room() view (single room detail)."""

    def test_room_view_returns_200_authenticated(self, authenticated_client):
        """Test room view returns HTTP 200 for an authenticated user."""
        room = RoomFactory(name="TestRoom", slug="test-room")
        response = authenticated_client.get(reverse("room", kwargs={"slug": room.slug}))
        assert response.status_code == 200

    def test_room_view_uses_correct_template(self, authenticated_client):
        """Test room view renders the 'room.html' template."""
        room = RoomFactory(name="TestRoom", slug="test-room")
        response = authenticated_client.get(reverse("room", kwargs={"slug": room.slug}))
        assert "room.html" in [t.name for t in response.templates]

    def test_room_view_context_room_name(self, authenticated_client):
        """Test room view context contains correct room_name."""
        room = RoomFactory(name="TestRoom", slug="test-room")
        response = authenticated_client.get(reverse("room", kwargs={"slug": room.slug}))
        assert response.context["room_name"] == "TestRoom"

    def test_room_view_context_slug(self, authenticated_client):
        """Test room view context contains correct slug."""
        room = RoomFactory(name="TestRoom", slug="test-room")
        response = authenticated_client.get(reverse("room", kwargs={"slug": room.slug}))
        assert response.context["slug"] == "test-room"

    def test_room_view_context_messages(self, authenticated_client):
        """Test room view context contains messages for the room."""
        room = RoomFactory(name="TestRoom", slug="test-room")
        user = UserFactory()
        msg1 = MessageFactory(user=user, room=room, content="Hello")
        msg2 = MessageFactory(user=user, room=room, content="World")
        # Create a message in a different room (should not appear)
        other_room = RoomFactory(name="Other", slug="other")
        MessageFactory(user=user, room=other_room, content="Not here")

        response = authenticated_client.get(reverse("room", kwargs={"slug": room.slug}))
        messages_in_context = list(response.context["messages"])
        assert msg1 in messages_in_context
        assert msg2 in messages_in_context
        assert len(messages_in_context) == 2

    def test_room_view_empty_messages(self, authenticated_client):
        """Test room view with no messages shows empty queryset."""
        room = RoomFactory(name="EmptyRoom", slug="empty-room")
        response = authenticated_client.get(reverse("room", kwargs={"slug": room.slug}))
        messages_in_context = list(response.context["messages"])
        assert len(messages_in_context) == 0
