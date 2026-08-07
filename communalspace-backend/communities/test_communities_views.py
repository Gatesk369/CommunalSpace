from accounts.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from communities.models import Community, CommunityAdminApplication


def create_user(email, role="resident", password="testpass123", **kwargs):
    return User.objects.create_user(
        email=email,
        password=password,
        first_name="Test",
        last_name="User",
        role=role,
        is_active=True,
        **kwargs,
    )


def create_community(name="Test Community", admin=None, applications_open=False):
    community = Community.objects.create(
        name=name,
        city="Test City",
        address="123 Test St",
        applications_open=applications_open,
    )
    if admin is not None:
        community.admins.add(admin)
    return community


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
        response = self.client.get(
            reverse("community-detail", args=[self.community.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


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


class CommunityUpdateDeleteViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.community_admin = create_user("cadmin@test.com", role="community admin")
        self.resident = create_user("resident@test.com", role="resident")
        self.community = create_community(admin=self.community_admin)

    def test_community_admin_can_update_own_community(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("community-update", args=[self.community.pk]),
            {"name": "Updated Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resident_cannot_update_community(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("community-update", args=[self.community.pk]),
            {"name": "Hacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_community(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.delete(
            reverse("community-delete", args=[self.community.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_resident_cannot_delete_community(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.delete(
            reverse("community-delete", args=[self.community.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommunityApplicationSeasonViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.resident = create_user("resident@test.com", role="resident")
        self.community = create_community(applications_open=False)

    def test_admin_can_open_applications(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("community-application-season", args=[self.community.pk]),
            {"action": "open"},
            format="json",
        )
        self.community.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.community.applications_open)

    def test_resident_cannot_open_applications(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("community-application-season", args=[self.community.pk]),
            {"action": "open"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_can_get_season_status(self):
        self.client.force_authenticate(user=self.resident)
        response = self.client.get(
            reverse("community-application-season", args=[self.community.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["applications_open"])


class CommunityAdminApplicationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.resident = create_user("resident@test.com", role="resident")
        self.community = create_community(applications_open=True)

    def test_resident_can_apply_when_open(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("community-apply", args=[self.community.pk]),
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CommunityAdminApplication.objects.count(), 1)

    def test_cannot_apply_when_closed(self):
        self.community.applications_open = False
        self.community.save()
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("community-apply", args=[self.community.pk]),
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_list_applications(self):
        CommunityAdminApplication.objects.create(
            applicant=self.resident, community=self.community
        )
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("community-apply", args=[self.community.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_resident_cannot_list_applications(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("community-apply", args=[self.community.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommunityAdminApplicationReviewViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.resident = create_user("resident@test.com", role="resident")
        self.community = create_community(applications_open=True)
        self.application = CommunityAdminApplication.objects.create(
            applicant=self.resident, community=self.community
        )

    def test_admin_can_approve_application(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse(
                "community-application-review",
                args=[self.community.pk, self.application.pk],
            ),
            {"action": "approve"},
            format="json",
        )
        self.application.refresh_from_db()
        self.resident.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.application.status, CommunityAdminApplication.APPROVED)
        self.assertEqual(self.resident.role, "community admin")
        self.assertTrue(self.community.admins.filter(pk=self.resident.pk).exists())

    def test_admin_can_reject_application(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse(
                "community-application-review",
                args=[self.community.pk, self.application.pk],
            ),
            {"action": "reject"},
            format="json",
        )
        self.application.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.application.status, CommunityAdminApplication.REJECTED)

    def test_resident_cannot_review_application(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse(
                "community-application-review",
                args=[self.community.pk, self.application.pk],
            ),
            {"action": "approve"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommunityMembershipViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.resident = create_user("resident@test.com", role="resident")
        self.community = create_community()
        self.other_community = create_community(name="Other Community")

    def test_user_can_join_community(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.post(reverse("community-join", args=[self.community.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resident.refresh_from_db()
        self.assertEqual(self.resident.community, self.community)

    def test_joining_new_community_leaves_old_one(self):
        self.resident.community = self.community
        self.resident.save()
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        self.client.post(reverse("community-join", args=[self.other_community.pk]))
        self.resident.refresh_from_db()
        self.assertEqual(self.resident.community, self.other_community)

    def test_user_can_leave_community(self):
        self.resident.community = self.community
        self.resident.save()
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("community-leave", args=[self.community.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resident.refresh_from_db()
        self.assertIsNone(self.resident.community)

    def test_cannot_leave_community_you_are_not_in(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("community-leave", args=[self.community.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
