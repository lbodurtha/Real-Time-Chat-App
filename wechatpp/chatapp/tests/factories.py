import factory
from django.contrib.auth.models import User
from chatapp.models import Room, Message


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    name = factory.Sequence(lambda n: f"Room {n}")
    slug = factory.Sequence(lambda n: f"room-{n}")


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    user = factory.SubFactory(UserFactory)
    room = factory.SubFactory(RoomFactory)
    content = factory.Faker("sentence")
