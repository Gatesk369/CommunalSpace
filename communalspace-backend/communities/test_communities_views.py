from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from communities.models import Community


def create_user(email, role="resident", password="testpass123", **kwargs):
    return User.objects.create_user(
        email=email,
        password=password,
        first_name="Test",
        last_name="User",
        role=role,
        **kwargs,
    )


def create_community(name="Test Community", admin=None):
    return Community.objects.create(
        name=name,
        city="Test City",
        address="123 Test St",
        admin=admin,
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


class CommunityListDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.resident = create_user("resident@test.com", role="resident")
        self.community = create_community()

    def test_authenticated_user_can_list_communities(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("community-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_list_communities(self):
        response = self.client.get(reverse("community-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_view_community_detail(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("community-detail", args=[self.community.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_404_for_nonexistent_community(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("community-detail", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommunityCreateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.resident = create_user("resident@test.com", role="resident")

    def test_admin_can_create_community(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("community-create"),
            {"name": "New Community", "city": "Kampala", "address": "123 Main St"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_resident_cannot_create_community(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("community-create"),
            {"name": "New Community", "city": "Kampala", "address": "123 Main St"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_community(self):
        response = self.client.post(
            reverse("community-create"),
            {"name": "New Community", "city": "Kampala", "address": "123 Main St"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CommunityUpdateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.community_admin = create_user("cadmin@test.com", role="community admin")
        self.other_community_admin = create_user("other_cadmin@test.com", role="community admin")
        self.resident = create_user("resident@test.com", role="resident")
        self.community = create_community(admin=self.community_admin)

    def test_platform_admin_can_update_community(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("community-update", args=[self.community.pk]),
            {"name": "Updated Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_community_admin_can_update_own_community(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("community-update", args=[self.community.pk]),
            {"name": "Updated Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_community_admin_cannot_update_other_community(self):
        token = get_token(self.client, "other_cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("community-update", args=[self.community.pk]),
            {"name": "Hacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_cannot_update_community(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("community-update", args=[self.community.pk]),
            {"name": "Hacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommunityDeleteViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.resident = create_user("resident@test.com", role="resident")
        self.community = create_community()

    def test_admin_can_delete_community(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.delete(reverse("community-delete", args=[self.community.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_resident_cannot_delete_community(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.delete(reverse("community-delete", args=[self.community.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)