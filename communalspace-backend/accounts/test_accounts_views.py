from communities.models import Community
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User


def create_user(email, role="resident", password="testpass123", **kwargs):
    return User.objects.create_user(
        email=email,
        password=password,
        first_name="Test",
        last_name="User",
        role=role,
        is_active=True,  # bypass email verification in tests
        **kwargs,
    )


def get_token(client, email, password="testpass123"):
    response = client.post(
        reverse("token_obtain_pair"),
        {"email": email, "password": password},
        format="json",
    )
    return response.data["access"]


def auth_client(client, token):
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class UserListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.resident = create_user("resident@test.com", role="resident")

    def test_admin_can_list_users(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resident_cannot_list_users(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_users(self):
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.resident = create_user("resident@test.com", role="resident")
        self.other = create_user("other@test.com", role="resident")

    def test_user_can_view_own_profile(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("user-detail", args=[self.resident.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_view_any_profile(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("user-detail", args=[self.resident.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_view_other_profile(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("user-detail", args=[self.other.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_404_for_nonexistent_user(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("user-detail", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserCreateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_anyone_can_register(self):
        response = self.client.post(
            reverse("user-create"),
            {
                "email": "new@test.com",
                "password": "testpass123",
                "first_name": "New",
                "last_name": "User",
                "role": "resident",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_data_returns_400(self):
        response = self.client.post(
            reverse("user-create"),
            {"email": "notanemail", "password": ""},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserUpdateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.resident = create_user("resident@test.com", role="resident")
        self.other = create_user("other@test.com", role="resident")

    def test_user_can_update_own_profile(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("user-update", args=[self.resident.pk]),
            {"first_name": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_any_profile(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("user-update", args=[self.resident.pk]),
            {"first_name": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_update_other_profile(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("user-update", args=[self.other.pk]),
            {"first_name": "Hacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserDeleteViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.resident = create_user("resident@test.com", role="resident")
        self.other = create_user("other@test.com", role="resident")

    def test_user_can_delete_own_account(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.delete(reverse("user-delete", args=[self.resident.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_delete_any_account(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.delete(reverse("user-delete", args=[self.resident.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cannot_delete_other_account(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.delete(reverse("user-delete", args=[self.other.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CurrentUserViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.community = Community.objects.create(
            name="Test Community",
            city="Kampala",
            address="Test Address",
        )

        self.user = User.objects.create_user(
            email="currentuser@example.com",
            password="password123",
            first_name="Current",
            last_name="User",
            role=User.RESIDENT,
            community=self.community,
            is_active=True,
        )

    def test_requires_authentication(self):
        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_authenticated_users_own_data(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["email"], "currentuser@example.com")

    def test_includes_community_id(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["community"], self.community.id)

    def test_does_not_expose_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("current-user"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("password", response.data)
