from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from communities.models import Community
from businesses.models import Business, BusinessBranch


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
    community = Community.objects.create(
        name=name,
        city="Test City",
        address="123 Test St",
    )
    if admin is not None:
        community.admins.add(admin)

    return community


def create_business(
    name="Test Business", owner=None, community=None, status=Business.APPROVED
):
    return Business.objects.create(
        name=name,
        owner=owner,
        community=community,
        status=status,
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


def create_branch(business, community, status=BusinessBranch.PENDING):
    return BusinessBranch.objects.create(
        business=business,
        community=community,
        address="123 Main St",
        city="Kampala",
        contact_phone="0700000000",
        contact_email="branch@test.com",
        status=status,
    )


class BusinessBranchApprovalViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.community_admin = create_user("cadmin@test.com", role="community admin")
        self.other_community_admin = create_user(
            "other_cadmin@test.com", role="community admin"
        )
        self.resident = create_user("resident@test.com", role="resident")
        self.owner = create_user("owner@test.com", role="business owner")
        self.community = create_community(admin=self.community_admin)
        self.other_community = create_community(
            name="Other Community", admin=self.other_community_admin
        )
        self.business = create_business(
            owner=self.owner, community=self.community, status=Business.APPROVED
        )
        self.pending_branch = create_branch(
            business=self.business, community=self.community
        )

    def test_community_admin_can_see_pending_branches(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("branch-pending"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resident_cannot_see_pending_branches(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("branch-pending"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_community_admin_can_approve_branch(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("branch-review", args=[self.pending_branch.pk]),
            {"action": "approve"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending_branch.refresh_from_db()
        self.assertEqual(self.pending_branch.status, BusinessBranch.APPROVED)

    def test_community_admin_can_reject_branch(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("branch-review", args=[self.pending_branch.pk]),
            {"action": "reject", "rejection_reason": "Invalid location"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending_branch.refresh_from_db()
        self.assertEqual(self.pending_branch.status, BusinessBranch.REJECTED)
        self.assertEqual(self.pending_branch.rejection_reason, "Invalid location")

    def test_other_community_admin_cannot_review_branch(self):
        token = get_token(self.client, "other_cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("branch-review", args=[self.pending_branch.pk]),
            {"action": "approve"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_action_returns_400(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("branch-review", args=[self.pending_branch.pk]),
            {"action": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_business_approval_also_approves_first_branch(self):
        # create a pending business with a branch
        pending_business = create_business(
            owner=self.owner, community=self.community, status=Business.PENDING
        )
        branch = create_branch(business=pending_business, community=self.community)
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        self.client.post(
            reverse("business-review", args=[pending_business.pk]),
            {"action": "approve"},
            format="json",
        )
        branch.refresh_from_db()
        self.assertEqual(branch.status, BusinessBranch.APPROVED)

    def test_business_rejection_also_rejects_first_branch(self):
        pending_business = create_business(
            owner=self.owner, community=self.community, status=Business.PENDING
        )
        branch = create_branch(business=pending_business, community=self.community)
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        self.client.post(
            reverse("business-review", args=[pending_business.pk]),
            {"action": "reject", "rejection_reason": "Fake business"},
            format="json",
        )
        branch.refresh_from_db()
        self.assertEqual(branch.status, BusinessBranch.REJECTED)


class BusinessListDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.community_admin = create_user("cadmin@test.com", role="community admin")
        self.resident = create_user("resident@test.com", role="resident")
        self.community = create_community(admin=self.community_admin)
        self.approved_business = create_business(
            name="Approved", community=self.community, status=Business.APPROVED
        )
        self.pending_business = create_business(
            name="Pending", community=self.community, status=Business.PENDING
        )

    def test_resident_sees_only_approved_businesses(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("business-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [b["name"] for b in response.data]
        self.assertIn("Approved", names)
        self.assertNotIn("Pending", names)

    def test_community_admin_sees_all_businesses_in_their_community(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("business-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [b["name"] for b in response.data]
        self.assertIn("Approved", names)
        self.assertIn("Pending", names)

    def test_unauthenticated_cannot_list_businesses(self):
        response = self.client.get(reverse("business-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_resident_cannot_access_pending_business_directly(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(
            reverse("business-detail", args=[self.pending_business.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_resident_can_access_approved_business_directly(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(
            reverse("business-detail", args=[self.approved_business.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BusinessCreateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.resident = create_user("resident@test.com", role="resident")
        self.community = create_community()
        self.business_payload = {
            "name": "My Shop",
            "community": self.community.pk,
            "branch": {
                "address": "123 Main St",
                "city": "Kampala",
                "contact_phone": "0700000000",
                "contact_email": "myshop@email.com",
            },
        }

    def test_authenticated_user_can_submit_business(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-create"),
            self.business_payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_business_is_pending_on_creation(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-create"),
            self.business_payload,
            format="json",
        )
        self.assertEqual(response.data["status"], Business.PENDING)

    def test_unauthenticated_cannot_create_business(self):
        response = self.client.post(
            reverse("business-create"),
            self.business_payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BusinessApprovalViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.community_admin = create_user("cadmin@test.com", role="community admin")
        self.other_community_admin = create_user(
            "other_cadmin@test.com", role="community admin"
        )
        self.resident = create_user("resident@test.com", role="resident")
        self.business_owner = create_user("owner@test.com", role="resident")
        self.community = create_community(admin=self.community_admin)
        self.other_community = create_community(
            name="Other Community", admin=self.other_community_admin
        )
        self.pending_business = create_business(
            name="Pending Shop",
            owner=self.business_owner,
            community=self.community,
            status=Business.PENDING,
        )

    def test_community_admin_can_see_pending_businesses(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("business-pending"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resident_cannot_see_pending_businesses(self):
        token = get_token(self.client, "resident@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("business-pending"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_community_admin_can_approve_business(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-review", args=[self.pending_business.pk]),
            {"action": "approve"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending_business.refresh_from_db()
        self.assertEqual(self.pending_business.status, Business.APPROVED)

    def test_approval_upgrades_owner_role(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        self.client.post(
            reverse("business-review", args=[self.pending_business.pk]),
            {"action": "approve"},
            format="json",
        )
        self.business_owner.refresh_from_db()
        self.assertEqual(self.business_owner.role, "business owner")

    def test_community_admin_can_reject_business(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-review", args=[self.pending_business.pk]),
            {"action": "reject", "rejection_reason": "Not a real business"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending_business.refresh_from_db()
        self.assertEqual(self.pending_business.status, Business.REJECTED)
        self.assertEqual(self.pending_business.rejection_reason, "Not a real business")

    def test_other_community_admin_cannot_review_business(self):
        token = get_token(self.client, "other_cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-review", args=[self.pending_business.pk]),
            {"action": "approve"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_action_returns_400(self):
        token = get_token(self.client, "cadmin@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-review", args=[self.pending_business.pk]),
            {"action": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BusinessUpdateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.owner = create_user("owner@test.com", role="business owner")
        self.other = create_user("other@test.com", role="resident")
        self.community = create_community()
        self.business = create_business(owner=self.owner, community=self.community)

    def test_owner_can_update_own_business(self):
        token = get_token(self.client, "owner@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("business-update", args=[self.business.pk]),
            {"name": "Updated Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_any_business(self):
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("business-update", args=[self.business.pk]),
            {"name": "Updated Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cannot_update_business(self):
        token = get_token(self.client, "other@test.com")
        auth_client(self.client, token)
        response = self.client.patch(
            reverse("business-update", args=[self.business.pk]),
            {"name": "Hacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BusinessDeleteViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_user("admin@test.com", role="admin")
        self.owner = create_user("owner@test.com", role="business owner")
        self.other = create_user("other@test.com", role="resident")
        self.community = create_community()

    def test_owner_can_delete_own_business(self):
        business = create_business(owner=self.owner, community=self.community)
        token = get_token(self.client, "owner@test.com")
        auth_client(self.client, token)
        response = self.client.delete(reverse("business-delete", args=[business.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_delete_any_business(self):
        business = create_business(owner=self.owner, community=self.community)
        token = get_token(self.client, "admin@test.com")
        auth_client(self.client, token)
        response = self.client.delete(reverse("business-delete", args=[business.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_owner_cannot_delete_business(self):
        business = create_business(owner=self.owner, community=self.community)
        token = get_token(self.client, "other@test.com")
        auth_client(self.client, token)
        response = self.client.delete(reverse("business-delete", args=[business.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
