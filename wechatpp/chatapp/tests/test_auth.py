import pytest
from django.urls import reverse

from chatapp.tests.factories import UserFactory


@pytest.mark.django_db
class TestLoginPage:
    """Tests for the login page accessibility."""

    def test_login_page_accessible(self, client):
        """Test that GET /accounts/login/ returns HTTP 200."""
        response = client.get(reverse("login"))
        assert response.status_code == 200

    def test_login_page_uses_login_template(self, client):
        """Test that the login page renders the login template."""
        response = client.get(reverse("login"))
        template_names = [t.name for t in response.templates]
        assert "registration/login.html" in template_names


@pytest.mark.django_db
class TestLoginAuthentication:
    """Tests for login with valid and invalid credentials."""

    def test_login_valid_credentials_redirects(self, client):
        """Test that logging in with valid credentials redirects to '/'."""
        user = UserFactory(username="validuser")
        response = client.post(
            reverse("login"),
            {"username": "validuser", "password": "testpass123"},
        )
        # LOGIN_REDIRECT_URL is "/" so expect a redirect
        assert response.status_code == 302
        assert response.url == "/"

    def test_login_invalid_credentials_shows_form(self, client):
        """Test that logging in with invalid credentials re-renders the form (200)."""
        UserFactory(username="validuser")
        response = client.post(
            reverse("login"),
            {"username": "validuser", "password": "wrongpassword"},
        )
        # Invalid login stays on the login page (200, not a redirect)
        assert response.status_code == 200


@pytest.mark.django_db
class TestAuthenticatedAccess:
    """Tests for authenticated vs. unauthenticated access to rooms."""

    def test_unauthenticated_shows_not_logged_in(self, client):
        """Test that an unauthenticated user sees 'You are not logged in' on rooms page."""
        response = client.get(reverse("rooms"))
        content = response.content.decode()
        assert "You are not logged in" in content

    def test_authenticated_shows_room_listing(self, authenticated_client):
        """Test that an authenticated user sees the room listing content."""
        response = authenticated_client.get(reverse("rooms"))
        content = response.content.decode()
        assert "Welcome to Chatapp" in content

    def test_authenticated_does_not_show_not_logged_in(self, authenticated_client):
        """Test that an authenticated user does NOT see 'not logged in' message."""
        response = authenticated_client.get(reverse("rooms"))
        content = response.content.decode()
        assert "You are not logged in" not in content
