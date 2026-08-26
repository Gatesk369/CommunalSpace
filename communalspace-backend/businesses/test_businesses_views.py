from accounts.models import User
from communities.models import Community
from django.test import TestCase
from django.urls import reverse
from notifications.models import Notification
from rest_framework import status
from rest_framework.test import APIClient

from businesses.models import Business, BusinessBranch, BusinessRating, Follow


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


class BusinessRatingViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rater_1 = create_user("rater1@test.com", role="resident")
        self.rater_2 = create_user("rater2@test.com", role="resident")
        self.owner = create_user("owner@test.com", role="business owner")
        self.community = create_community()
        self.business = create_business(
            name="Rateable Shop",
            owner=self.owner,
            community=self.community,
            status=Business.APPROVED,
        )
        self.pending_business = create_business(
            name="Pending Shop",
            owner=self.owner,
            community=self.community,
            status=Business.PENDING,
        )

    # ---------------------------------------------------------
    # RATE
    # ---------------------------------------------------------

    def test_unauthenticated_cannot_rate_business(self):
        response = self.client.post(
            reverse("business-rate", args=[self.business.pk]),
            {"stars": 8},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_rate_business(self):
        token = get_token(self.client, "rater1@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-rate", args=[self.business.pk]),
            {"stars": 8},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            BusinessRating.objects.filter(
                business=self.business, user=self.rater_1, stars=8
            ).exists()
        )

    def test_rating_again_updates_existing_rating_instead_of_duplicating(self):
        token = get_token(self.client, "rater1@test.com")
        auth_client(self.client, token)

        self.client.post(
            reverse("business-rate", args=[self.business.pk]),
            {"stars": 6},
            format="json",
        )
        response = self.client.post(
            reverse("business-rate", args=[self.business.pk]),
            {"stars": 10},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            BusinessRating.objects.filter(
                business=self.business, user=self.rater_1
            ).count(),
            1,
        )
        rating = BusinessRating.objects.get(business=self.business, user=self.rater_1)
        self.assertEqual(rating.stars, 10)

    def test_cannot_rate_unapproved_business(self):
        token = get_token(self.client, "rater1@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-rate", args=[self.pending_business.pk]),
            {"stars": 8},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_rating_rejects_non_integer_input(self):
        token = get_token(self.client, "rater1@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-rate", args=[self.business.pk]),
            {"stars": "amazing"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_rejects_zero(self):
        token = get_token(self.client, "rater1@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-rate", args=[self.business.pk]),
            {"stars": 0},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_rejects_above_ten(self):
        token = get_token(self.client, "rater1@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-rate", args=[self.business.pk]),
            {"stars": 11},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------
    # UNRATE
    # ---------------------------------------------------------

    def test_user_can_unrate_business(self):
        token = get_token(self.client, "rater1@test.com")
        auth_client(self.client, token)

        self.client.post(
            reverse("business-rate", args=[self.business.pk]),
            {"stars": 8},
            format="json",
        )
        response = self.client.delete(
            reverse("business-unrate", args=[self.business.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            BusinessRating.objects.filter(
                business=self.business, user=self.rater_1
            ).exists()
        )

    def test_unrating_without_existing_rating_returns_404(self):
        token = get_token(self.client, "rater1@test.com")
        auth_client(self.client, token)
        response = self.client.delete(
            reverse("business-unrate", args=[self.business.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------------------------------------------------------
    # AGGREGATION
    # ---------------------------------------------------------

    def test_business_detail_shows_no_rating_when_unrated(self):
        token = get_token(self.client, "rater1@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("business-detail", args=[self.business.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["average_rating"])
        self.assertEqual(response.data["rating_count"], 0)

    def test_business_detail_shows_correct_average_across_multiple_raters(self):
        BusinessRating.objects.create(
            business=self.business, user=self.rater_1, stars=8
        )
        BusinessRating.objects.create(
            business=self.business, user=self.rater_2, stars=10
        )

        token = get_token(self.client, "rater1@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("business-detail", args=[self.business.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # (8 + 10) / 2 = 9 -> 4.5 stars
        self.assertEqual(response.data["average_rating"], 4.5)
        self.assertEqual(response.data["rating_count"], 2)

    def test_business_list_includes_rating_fields(self):
        BusinessRating.objects.create(
            business=self.business, user=self.rater_1, stars=9
        )

        token = get_token(self.client, "rater1@test.com")
        auth_client(self.client, token)
        response = self.client.get(reverse("business-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rated = next(b for b in response.data if b["name"] == "Rateable Shop")
        self.assertEqual(rated["average_rating"], 4.5)
        self.assertEqual(rated["rating_count"], 1)


class FollowToggleViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.follower = create_user("follower@test.com", role="resident")
        self.owner = create_user("owner@test.com", role="business owner")
        self.community = create_community()
        self.business = create_business(
            name="Followable Shop",
            owner=self.owner,
            community=self.community,
            status=Business.APPROVED,
        )
        self.pending_business = create_business(
            name="Pending Shop",
            owner=self.owner,
            community=self.community,
            status=Business.PENDING,
        )

    def test_unauthenticated_cannot_follow(self):
        response = self.client.post(reverse("business-follow", args=[self.business.pk]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_follow_business(self):
        token = get_token(self.client, "follower@test.com")
        auth_client(self.client, token)
        response = self.client.post(reverse("business-follow", args=[self.business.pk]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Follow.objects.filter(
                follower=self.follower, business=self.business
            ).exists()
        )

    def test_following_again_unfollows(self):
        token = get_token(self.client, "follower@test.com")
        auth_client(self.client, token)
        self.client.post(reverse("business-follow", args=[self.business.pk]))
        response = self.client.post(reverse("business-follow", args=[self.business.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Follow.objects.filter(
                follower=self.follower, business=self.business
            ).exists()
        )

    def test_cannot_follow_unapproved_business(self):
        token = get_token(self.client, "follower@test.com")
        auth_client(self.client, token)
        response = self.client.post(
            reverse("business-follow", args=[self.pending_business.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FollowNotificationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.follower = create_user("follower@test.com", role="resident")
        self.owner = create_user("owner@test.com", role="business owner")
        self.community = create_community()
        self.business = create_business(
            name="Followable Shop",
            owner=self.owner,
            community=self.community,
            status=Business.APPROVED,
        )

    def test_following_notifies_business_owner(self):
        token = get_token(self.client, "follower@test.com")
        auth_client(self.client, token)
        self.client.post(reverse("business-follow", args=[self.business.pk]))
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.owner, notification_type=Notification.NEW_FOLLOWER
            ).exists()
        )

    def test_unfollowing_does_not_notify(self):
        token = get_token(self.client, "follower@test.com")
        auth_client(self.client, token)
        self.client.post(reverse("business-follow", args=[self.business.pk]))
        Notification.objects.filter(
            notification_type=Notification.NEW_FOLLOWER
        ).delete()

        self.client.post(
            reverse("business-follow", args=[self.business.pk])
        )  # unfollow

        self.assertFalse(
            Notification.objects.filter(
                notification_type=Notification.NEW_FOLLOWER
            ).exists()
        )

    def test_notification_message_includes_business_name(self):
        token = get_token(self.client, "follower@test.com")
        auth_client(self.client, token)
        self.client.post(reverse("business-follow", args=[self.business.pk]))
        notification = Notification.objects.get(
            recipient=self.owner, notification_type=Notification.NEW_FOLLOWER
        )
        self.assertIn("Followable Shop", notification.message)

    def test_notification_has_business_fk(self):
        token = get_token(self.client, "follower@test.com")
        auth_client(self.client, token)
        self.client.post(reverse("business-follow", args=[self.business.pk]))

        notification = Notification.objects.get(
            recipient=self.owner, notification_type=Notification.NEW_FOLLOWER
        )
        self.assertEqual(notification.business, self.business)
