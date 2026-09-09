import json

import pytest
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test import override_settings

from wechatpp.consumers import ChatConsumer
from chatapp.models import Room, Message
from chatapp.tests.factories import UserFactory, RoomFactory


CHANNEL_LAYERS_SETTING = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}


def _make_communicator(room_slug="test-room"):
    """Create a WebsocketCommunicator for ChatConsumer with the given room slug."""
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), f"/ws/{room_slug}/")
    communicator.scope["url_route"] = {"kwargs": {"room_slug": room_slug}}
    return communicator


@pytest.mark.django_db(transaction=True)
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_SETTING)
class TestChatConsumerConnect:
    """Tests for ChatConsumer WebSocket connection."""

    async def test_consumer_connect_accepts(self):
        """Test that the consumer accepts a WebSocket connection."""
        communicator = _make_communicator()
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    async def test_consumer_disconnect(self):
        """Test that the consumer disconnects cleanly."""
        communicator = _make_communicator()
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()
        # No exception means clean disconnect


@pytest.mark.django_db(transaction=True)
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_SETTING)
class TestChatConsumerMessaging:
    """Tests for ChatConsumer message send/receive flow."""

    async def test_send_receive_message(self):
        """Test sending a message and receiving the echo back via group."""
        user = await database_sync_to_async(UserFactory)()
        room = await database_sync_to_async(RoomFactory)(name="TestRoom", slug="test-room")

        communicator = _make_communicator(room_slug="test-room")
        connected, _ = await communicator.connect()
        assert connected is True

        # Send a message
        await communicator.send_json_to({
            "message": "Hello, world!",
            "username": user.username,
            "room_name": "TestRoom",
        })

        # Receive the echoed message
        response = await communicator.receive_json_from(timeout=5)
        assert response["message"] == "Hello, world!"
        assert response["username"] == user.username

        await communicator.disconnect()

    async def test_message_json_structure(self):
        """Test that received messages have the expected JSON structure."""
        user = await database_sync_to_async(UserFactory)()
        await database_sync_to_async(RoomFactory)(name="TestRoom", slug="test-room")

        communicator = _make_communicator(room_slug="test-room")
        await communicator.connect()

        await communicator.send_json_to({
            "message": "Test content",
            "username": user.username,
            "room_name": "TestRoom",
        })

        response = await communicator.receive_json_from(timeout=5)
        assert "message" in response
        assert "username" in response

        await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_SETTING)
class TestChatConsumerGroupMessaging:
    """Tests for group messaging between multiple consumers in the same room."""

    async def test_group_message_broadcast(self):
        """Test that a message sent by one consumer is received by another in the same room."""
        user = await database_sync_to_async(UserFactory)()
        await database_sync_to_async(RoomFactory)(name="TestRoom", slug="test-room")

        # Two communicators join the same room
        communicator1 = _make_communicator(room_slug="test-room")
        communicator2 = _make_communicator(room_slug="test-room")

        connected1, _ = await communicator1.connect()
        connected2, _ = await communicator2.connect()
        assert connected1 is True
        assert connected2 is True

        # Consumer 1 sends a message
        await communicator1.send_json_to({
            "message": "Hello from user 1",
            "username": user.username,
            "room_name": "TestRoom",
        })

        # Both consumers should receive the message
        response1 = await communicator1.receive_json_from(timeout=5)
        response2 = await communicator2.receive_json_from(timeout=5)

        assert response1["message"] == "Hello from user 1"
        assert response2["message"] == "Hello from user 1"

        await communicator1.disconnect()
        await communicator2.disconnect()


@pytest.mark.django_db(transaction=True)
@override_settings(CHANNEL_LAYERS=CHANNEL_LAYERS_SETTING)
class TestChatConsumerSaveMessage:
    """Tests for the save_message functionality of ChatConsumer."""

    async def test_save_message_creates_message_in_db(self):
        """Test that sending a message via WebSocket creates a Message object in the database."""
        user = await database_sync_to_async(UserFactory)()
        room = await database_sync_to_async(RoomFactory)(name="TestRoom", slug="test-room")

        communicator = _make_communicator(room_slug="test-room")
        await communicator.connect()

        await communicator.send_json_to({
            "message": "Persisted message",
            "username": user.username,
            "room_name": "TestRoom",
        })

        # Wait for the response to ensure processing is complete
        await communicator.receive_json_from(timeout=5)

        # Verify the message was saved to the database
        @database_sync_to_async
        def check_message():
            messages = Message.objects.filter(room=room, user=user)
            assert messages.count() == 1
            assert messages.first().content == "Persisted message"

        await check_message()

        await communicator.disconnect()

    async def test_save_message_correct_user_and_room(self):
        """Test that saved message is associated with the correct user and room."""
        user = await database_sync_to_async(UserFactory)()
        room = await database_sync_to_async(RoomFactory)(name="MyRoom", slug="my-room")

        communicator = _make_communicator(room_slug="my-room")
        await communicator.connect()

        await communicator.send_json_to({
            "message": "Check associations",
            "username": user.username,
            "room_name": "MyRoom",
        })

        await communicator.receive_json_from(timeout=5)

        @database_sync_to_async
        def verify_associations():
            msg = Message.objects.get(content="Check associations")
            assert msg.user.username == user.username
            assert msg.room.name == "MyRoom"
            assert msg.room.slug == "my-room"

        await verify_associations()

        await communicator.disconnect()
