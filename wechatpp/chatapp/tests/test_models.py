import pytest
from django.utils import timezone

from chatapp.models import Room, Message
from chatapp.tests.factories import UserFactory, RoomFactory, MessageFactory


@pytest.mark.django_db
class TestRoomModel:
    """Tests for the Room model."""

    def test_room_creation(self):
        """Test that a Room can be created with a name and slug."""
        room = RoomFactory(name="General", slug="general")
        assert room.pk is not None
        assert room.name == "General"
        assert room.slug == "general"

    def test_room_str_representation(self):
        """Test Room __str__ returns 'Room : {name} | Id : {slug}'."""
        room = RoomFactory(name="General", slug="general")
        assert str(room) == "Room : General | Id : general"

    def test_room_name_max_length(self):
        """Test Room name field has max_length=20."""
        name_field = Room._meta.get_field("name")
        assert name_field.max_length == 20

    def test_room_slug_max_length(self):
        """Test Room slug field has max_length=100."""
        slug_field = Room._meta.get_field("slug")
        assert slug_field.max_length == 100


@pytest.mark.django_db
class TestMessageModel:
    """Tests for the Message model."""

    def test_message_creation(self):
        """Test that a Message can be created with user, room, and content."""
        message = MessageFactory(content="Hello, world!")
        assert message.pk is not None
        assert message.content == "Hello, world!"
        assert message.user is not None
        assert message.room is not None

    def test_message_str_representation(self):
        """Test Message __str__ returns 'Message is :- {content}'."""
        message = MessageFactory(content="Test message")
        assert str(message) == "Message is :- Test message"

    def test_message_user_foreign_key(self):
        """Test Message has a FK relationship to User."""
        user = UserFactory()
        room = RoomFactory()
        message = MessageFactory(user=user, room=room)
        assert message.user == user
        assert message.user.pk == user.pk

    def test_message_room_foreign_key(self):
        """Test Message has a FK relationship to Room."""
        room = RoomFactory(name="TestRoom", slug="test-room")
        message = MessageFactory(room=room)
        assert message.room == room
        assert message.room.pk == room.pk

    def test_message_created_on_auto_now_add(self):
        """Test Message created_on is set automatically on creation."""
        before = timezone.now()
        message = MessageFactory()
        after = timezone.now()
        assert message.created_on is not None
        assert before <= message.created_on <= after

    def test_message_user_cascade_delete(self):
        """Test deleting a user cascades to delete their messages."""
        user = UserFactory()
        MessageFactory(user=user)
        assert Message.objects.filter(user=user).count() == 1
        user.delete()
        assert Message.objects.filter(user=user).count() == 0

    def test_message_room_cascade_delete(self):
        """Test deleting a room cascades to delete its messages."""
        room = RoomFactory()
        MessageFactory(room=room)
        assert Message.objects.filter(room=room).count() == 1
        room.delete()
        assert Message.objects.filter(room=room).count() == 0
