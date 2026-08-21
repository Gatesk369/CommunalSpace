from accounts.models import User
from communities.models import Community
from django.test import TestCase
from django.urls import reverse
from notifications.models import Notification
from rest_framework import status
from rest_framework.test import APIClient

from .models import Announcement


def create_user(email, role="resident", **kwargs):
    return User.objects.create_user(
        email=email,
        password="testpass123",
        first_name="Test",
        last_name="User",
        role=role,
        is_active=True,
        **kwargs,
    )


def create_community(name="Test Community", admins=None):
    community = Community.objects.create(
        name=name,
        city="Test City",
        address="123 Test St",
    )
    for admin in admins or []:
        community.admins.add(admin)
    return community


class AnnouncementAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.resident = create_user("resident@test.com", role="resident")
        self.platform_admin = create_user("platform@test.com", role="admin")

        self.community_admin_1 = create_user("cadmin1@test.com", role="community admin")
        self.community_admin_both = create_user(
            "cadminboth@test.com", role="community admin"
        )

        self.community_1 = create_community(
            "Community One", admins=[self.community_admin_1, self.community_admin_both]
        )
        self.community_2 = create_community(
            "Community Two", admins=[self.community_admin_both]
        )
        self.community_3 = create_community("Community Three")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def test_unauthenticated_cannot_create_announcement(self):
        response = self.client.post(
            reverse("announcement-create"),
            {
                "title": "Water outage",
                "content": "Water will be shut off tomorrow.",
                "urgency": Announcement.WARNING,
                "communities": [self.community_1.id],
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_resident_cannot_create_announcement(self):
        self.authenticate(self.resident)

        response = self.client.post(
            reverse("announcement-create"),
            {
                "title": "Water outage",
                "content": "Water will be shut off tomorrow.",
                "urgency": Announcement.WARNING,
                "communities": [self.community_1.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_community_admin_can_create_announcement_for_administered_community(self):
        self.authenticate(self.community_admin_1)

        response = self.client.post(
            reverse("announcement-create"),
            {
                "title": "Water outage",
                "content": "Water will be shut off tomorrow.",
                "urgency": Announcement.WARNING,
                "communities": [self.community_1.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        announcement = Announcement.objects.get(title="Water outage")
        self.assertEqual(list(announcement.communities.all()), [self.community_1])

    def test_community_admin_can_create_announcement_for_multiple_administered_communities(
        self,
    ):
        self.authenticate(self.community_admin_both)

        response = self.client.post(
            reverse("announcement-create"),
            {
                "title": "Block party",
                "content": "Annual block party in three weeks.",
                "urgency": Announcement.INFO,
                "communities": [self.community_1.id, self.community_2.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        announcement = Announcement.objects.get(title="Block party")
        self.assertEqual(announcement.communities.count(), 2)

    def test_community_admin_cannot_create_announcement_for_unadministered_community(
        self,
    ):
        self.authenticate(self.community_admin_1)

        response = self.client.post(
            reverse("announcement-create"),
            {
                "title": "Sneaky announcement",
                "content": "Shouldn't be allowed.",
                "urgency": Announcement.CRITICAL,
                "communities": [self.community_1.id, self.community_3.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            Announcement.objects.filter(title="Sneaky announcement").exists()
        )

    def test_platform_admin_can_create_announcement_for_any_community(self):
        self.authenticate(self.platform_admin)

        response = self.client.post(
            reverse("announcement-create"),
            {
                "title": "Platform-wide notice",
                "content": "Applies everywhere.",
                "urgency": Announcement.INFO,
                "communities": [self.community_1.id, self.community_3.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_requires_at_least_one_community(self):
        self.authenticate(self.community_admin_1)

        response = self.client.post(
            reverse("announcement-create"),
            {
                "title": "No target",
                "content": "This shouldn't save.",
                "urgency": Announcement.INFO,
                "communities": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------
    # LIST / DETAIL — open to everyone
    # ---------------------------------------------------------

    def test_unauthenticated_cannot_list_announcements(self):
        response = self.client.get(reverse("announcement-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_any_authenticated_user_sees_announcements_from_other_communities(self):
        announcement = Announcement.objects.create(
            title="Community Two only",
            content="Only tied to community two.",
            urgency=Announcement.INFO,
        )
        announcement.communities.add(self.community_2)

        self.authenticate(self.resident)

        response = self.client.get(reverse("announcement-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [a["title"] for a in response.data]
        self.assertIn("Community Two only", titles)

    def test_announcement_detail_open_to_any_authenticated_user(self):
        announcement = Announcement.objects.create(
            title="Detail test",
            content="Some content.",
            urgency=Announcement.CRITICAL,
        )
        announcement.communities.add(self.community_3)

        self.authenticate(self.resident)

        response = self.client.get(
            reverse("announcement-detail", args=[announcement.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Detail test")

    def test_announcement_detail_404_for_nonexistent(self):
        self.authenticate(self.resident)

        response = self.client.get(reverse("announcement-detail", args=[99999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------

    def test_resident_cannot_delete_announcement(self):
        announcement = Announcement.objects.create(
            title="Undeletable by resident",
            content="Content.",
            urgency=Announcement.INFO,
        )
        announcement.communities.add(self.community_1)

        self.authenticate(self.resident)

        response = self.client.delete(
            reverse("announcement-delete", args=[announcement.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Announcement.objects.filter(pk=announcement.pk).exists())

    def test_community_admin_can_delete_announcement_fully_within_their_scope(self):
        announcement = Announcement.objects.create(
            title="Deletable",
            content="Content.",
            urgency=Announcement.INFO,
        )
        announcement.communities.add(self.community_1)

        self.authenticate(self.community_admin_1)

        response = self.client.delete(
            reverse("announcement-delete", args=[announcement.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Announcement.objects.filter(pk=announcement.pk).exists())

    def test_community_admin_cannot_delete_announcement_spanning_unadministered_community(
        self,
    ):
        announcement = Announcement.objects.create(
            title="Multi-community, partial admin",
            content="Content.",
            urgency=Announcement.WARNING,
        )
        announcement.communities.add(self.community_1, self.community_3)

        self.authenticate(self.community_admin_1)

        response = self.client.delete(
            reverse("announcement-delete", args=[announcement.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Announcement.objects.filter(pk=announcement.pk).exists())

    def test_community_admin_who_administers_all_target_communities_can_delete(self):
        announcement = Announcement.objects.create(
            title="Multi-community, full admin",
            content="Content.",
            urgency=Announcement.WARNING,
        )
        announcement.communities.add(self.community_1, self.community_2)

        self.authenticate(self.community_admin_both)

        response = self.client.delete(
            reverse("announcement-delete", args=[announcement.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_platform_admin_can_delete_any_announcement(self):
        announcement = Announcement.objects.create(
            title="Platform deletable",
            content="Content.",
            urgency=Announcement.CRITICAL,
        )
        announcement.communities.add(self.community_1, self.community_3)

        self.authenticate(self.platform_admin)

        response = self.client.delete(
            reverse("announcement-delete", args=[announcement.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_nonexistent_announcement_returns_404(self):
        self.authenticate(self.community_admin_1)

        response = self.client.delete(reverse("announcement-delete", args=[99999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def test_community_admin_can_update_own_announcement(self):
        announcement = Announcement.objects.create(
            title="Original title",
            content="Original content.",
            urgency=Announcement.INFO,
        )
        announcement.communities.add(self.community_1)

        self.authenticate(self.community_admin_1)

        response = self.client.patch(
            reverse("announcement-update", args=[announcement.pk]),
            {"title": "Updated title", "urgency": Announcement.CRITICAL},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        announcement.refresh_from_db()
        self.assertEqual(announcement.title, "Updated title")
        self.assertEqual(announcement.urgency, Announcement.CRITICAL)

    def test_community_admin_cannot_update_announcement_outside_their_scope(self):
        announcement = Announcement.objects.create(
            title="Not yours",
            content="Content.",
            urgency=Announcement.INFO,
        )
        announcement.communities.add(self.community_3)

        self.authenticate(self.community_admin_1)

        response = self.client.patch(
            reverse("announcement-update", args=[announcement.pk]),
            {"title": "Hacked title"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        announcement.refresh_from_db()
        self.assertEqual(announcement.title, "Not yours")

    def test_community_admin_cannot_reassign_announcement_to_unadministered_community(
        self,
    ):
        announcement = Announcement.objects.create(
            title="Reassignment attempt",
            content="Content.",
            urgency=Announcement.INFO,
        )
        announcement.communities.add(self.community_1)

        self.authenticate(self.community_admin_1)

        response = self.client.patch(
            reverse("announcement-update", args=[announcement.pk]),
            {"communities": [self.community_1.id, self.community_3.id]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_cannot_update_announcement(self):
        announcement = Announcement.objects.create(
            title="Protected",
            content="Content.",
            urgency=Announcement.INFO,
        )
        announcement.communities.add(self.community_1)

        self.authenticate(self.resident)

        response = self.client.patch(
            reverse("announcement-update", args=[announcement.pk]),
            {"title": "Hacked"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_nonexistent_announcement_returns_404(self):
        self.authenticate(self.community_admin_1)

        response = self.client.patch(
            reverse("announcement-update", args=[99999]),
            {"title": "Doesn't matter"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AnnouncementNotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.community_admin_1 = create_user("cadmin1@test.com", role="community admin")
        self.community_1 = create_community(
            "Community One", admins=[self.community_admin_1]
        )
        self.community_2 = create_community("Community Two")

        self.member_1 = create_user(
            "member1@test.com", role="resident", community=self.community_1
        )
        self.member_2 = create_user(
            "member2@test.com", role="resident", community=self.community_1
        )
        self.outside_member = create_user(
            "outside@test.com", role="resident", community=self.community_2
        )
        self.communityless_user = create_user("nocommunity@test.com", role="resident")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_creating_announcement_notifies_community_members(self):
        self.authenticate(self.community_admin_1)

        response = self.client.post(
            reverse("announcement-create"),
            {
                "title": "Water outage",
                "content": "Water will be shut off tomorrow.",
                "urgency": Announcement.WARNING,
                "communities": [self.community_1.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.member_1, notification_type="announcement"
            ).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.member_2, notification_type="announcement"
            ).exists()
        )

    def test_notification_message_includes_title(self):
        self.authenticate(self.community_admin_1)

        self.client.post(
            reverse("announcement-create"),
            {
                "title": "Water outage",
                "content": "Water will be shut off tomorrow.",
                "urgency": Announcement.WARNING,
                "communities": [self.community_1.id],
            },
            format="json",
        )

        notification = Notification.objects.get(
            recipient=self.member_1, notification_type="announcement"
        )
        self.assertIn("Water outage", notification.message)

    def test_members_outside_targeted_community_not_notified(self):
        self.authenticate(self.community_admin_1)

        self.client.post(
            reverse("announcement-create"),
            {
                "title": "Water outage",
                "content": "Water will be shut off tomorrow.",
                "urgency": Announcement.WARNING,
                "communities": [self.community_1.id],
            },
            format="json",
        )

        self.assertFalse(
            Notification.objects.filter(
                recipient=self.outside_member, notification_type="announcement"
            ).exists()
        )

    def test_users_with_no_community_not_notified(self):
        self.authenticate(self.community_admin_1)

        self.client.post(
            reverse("announcement-create"),
            {
                "title": "Water outage",
                "content": "Water will be shut off tomorrow.",
                "urgency": Announcement.WARNING,
                "communities": [self.community_1.id],
            },
            format="json",
        )

        self.assertFalse(
            Notification.objects.filter(
                recipient=self.communityless_user, notification_type="announcement"
            ).exists()
        )

    def test_member_in_multiple_targeted_communities_notified_once(self):
        community_admin_both = create_user(
            "cadminboth@test.com", role="community admin"
        )
        self.community_1.admins.add(community_admin_both)
        self.community_2.admins.add(community_admin_both)

        dual_member = create_user(
            "dual@test.com", role="resident", community=self.community_1
        )

        self.authenticate(community_admin_both)

        self.client.post(
            reverse("announcement-create"),
            {
                "title": "Multi-community notice",
                "content": "Applies to both.",
                "urgency": Announcement.INFO,
                "communities": [self.community_1.id, self.community_2.id],
            },
            format="json",
        )

        self.assertEqual(
            Notification.objects.filter(
                recipient=dual_member, notification_type="announcement"
            ).count(),
            1,
        )

    def test_failed_creation_does_not_notify_anyone(self):
        self.authenticate(self.community_admin_1)

        response = self.client.post(
            reverse("announcement-create"),
            {
                "title": "Sneaky announcement",
                "content": "Shouldn't be allowed.",
                "urgency": Announcement.CRITICAL,
                "communities": [self.community_1.id, self.community_2.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            Notification.objects.filter(notification_type="announcement").exists()
        )
