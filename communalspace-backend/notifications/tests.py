import pytest
from accounts.models import User
from businesses.models import Business, BusinessBranch
from communities.models import Community
from rest_framework.test import APIClient

from notifications.models import Notification


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def community():
    return Community.objects.create(
        name="Test Community", city="Testville", address="123 Test St"
    )


@pytest.fixture
def user(community):
    return User.objects.create_user(
        email="resident@test.com",
        password="testpass123",
        first_name="Res",
        last_name="Ident",
        role="resident",
        is_active=True,
        community=community,
    )


@pytest.fixture
def other_user(community):
    return User.objects.create_user(
        email="other@test.com",
        password="testpass123",
        first_name="Other",
        last_name="User",
        role="resident",
        is_active=True,
        community=community,
    )


@pytest.fixture
def community_admin(community):
    admin = User.objects.create_user(
        email="admin@test.com",
        password="testpass123",
        first_name="Comm",
        last_name="Admin",
        role="community admin",
        is_active=True,
    )
    community.admins.add(admin)
    return admin


@pytest.fixture
def business(user, community):
    biz = Business.objects.create(name="Test Biz", owner=user, community=community)
    BusinessBranch.objects.create(
        business=biz,
        community=community,
        address="1 Branch Rd",
        city="Testville",
        contact_phone="1234567890",
        contact_email="branch@test.com",
    )
    return biz


@pytest.mark.django_db
class TestNotificationModel:
    def test_str_representation(self, user):
        notification = Notification.objects.create(
            recipient=user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="Your business was approved!",
        )
        assert str(notification) == f"business_approval -> {user}"

    def test_defaults(self, user):
        notification = Notification.objects.create(
            recipient=user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="Test message",
        )
        assert notification.is_read is False
        assert notification.created_at is not None

    def test_ordering_newest_first(self, user):
        first = Notification.objects.create(
            recipient=user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="First",
        )
        second = Notification.objects.create(
            recipient=user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="Second",
        )
        notifications = list(Notification.objects.all())
        assert notifications[0] == second
        assert notifications[1] == first


@pytest.mark.django_db
class TestNotificationListView:
    def test_requires_authentication(self, api_client):
        response = api_client.get("/api/v1/notifications/")
        assert response.status_code == 401

    def test_returns_only_own_notifications(self, api_client, user, other_user):
        Notification.objects.create(
            recipient=user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="Mine",
        )
        Notification.objects.create(
            recipient=other_user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="Not mine",
        )
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/notifications/")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["message"] == "Mine"

    def test_empty_list_when_no_notifications(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/notifications/")
        assert response.status_code == 200
        assert response.data == []


@pytest.mark.django_db
class TestNotificationMarkReadView:
    def test_marks_own_notification_read(self, api_client, user):
        notification = Notification.objects.create(
            recipient=user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="Test",
        )
        api_client.force_authenticate(user=user)
        response = api_client.patch(f"/api/v1/notifications/{notification.id}/read/")
        assert response.status_code == 200
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_cannot_mark_other_users_notification(self, api_client, user, other_user):
        notification = Notification.objects.create(
            recipient=other_user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="Not yours",
        )
        api_client.force_authenticate(user=user)
        response = api_client.patch(f"/api/v1/notifications/{notification.id}/read/")
        assert response.status_code == 404
        notification.refresh_from_db()
        assert notification.is_read is False

    def test_nonexistent_notification_returns_404(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.patch("/api/v1/notifications/99999/read/")
        assert response.status_code == 404

    def test_requires_authentication(self, api_client, user):
        notification = Notification.objects.create(
            recipient=user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="Test",
        )
        response = api_client.patch(f"/api/v1/notifications/{notification.id}/read/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestNotificationMarkAllReadView:
    def test_marks_all_unread_as_read(self, api_client, user):
        Notification.objects.create(
            recipient=user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="First",
        )
        Notification.objects.create(
            recipient=user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="Second",
        )
        api_client.force_authenticate(user=user)
        response = api_client.patch("/api/v1/notifications/mark-all-read/")
        assert response.status_code == 200
        assert Notification.objects.filter(recipient=user, is_read=False).count() == 0

    def test_does_not_affect_other_users_notifications(
        self, api_client, user, other_user
    ):
        other_notification = Notification.objects.create(
            recipient=other_user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="Not yours",
        )
        api_client.force_authenticate(user=user)
        api_client.patch("/api/v1/notifications/mark-all-read/")
        other_notification.refresh_from_db()
        assert other_notification.is_read is False

    def test_already_read_notifications_unaffected(self, api_client, user):
        notification = Notification.objects.create(
            recipient=user,
            notification_type=Notification.BUSINESS_APPROVAL,
            message="Test",
            is_read=True,
        )
        api_client.force_authenticate(user=user)
        response = api_client.patch("/api/v1/notifications/mark-all-read/")
        assert response.status_code == 200
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_approval_notification_message_and_business_fk_are_correct(
        self, api_client, community_admin, business
    ):
        api_client.force_authenticate(user=community_admin)
        api_client.post(
            f"/api/v1/businesses/review/{business.id}/", {"action": "approve"}
        )

        notification = Notification.objects.get(
            recipient=business.owner, notification_type=Notification.BUSINESS_APPROVAL
        )
        assert notification.business_id == business.id


@pytest.mark.django_db
class TestBusinessApprovalNotificationTrigger:
    def test_approval_creates_notification_for_owner(
        self, api_client, community_admin, business
    ):
        api_client.force_authenticate(user=community_admin)
        response = api_client.post(
            f"/api/v1/businesses/review/{business.id}/", {"action": "approve"}
        )
        assert response.status_code == 200
        notification = Notification.objects.filter(
            recipient=business.owner, notification_type=Notification.BUSINESS_APPROVAL
        ).first()
        assert notification is not None
        assert "approved" in notification.message.lower()

    def test_rejection_creates_notification_with_reason(
        self, api_client, community_admin, business
    ):
        api_client.force_authenticate(user=community_admin)
        response = api_client.post(
            f"/api/v1/businesses/review/{business.id}/",
            {"action": "reject", "rejection_reason": "Missing documentation"},
        )
        assert response.status_code == 200
        notification = Notification.objects.filter(
            recipient=business.owner, notification_type=Notification.BUSINESS_APPROVAL
        ).first()
        assert notification is not None
        assert "rejected" in notification.message.lower()
        assert "Missing documentation" in notification.message

    def test_approval_with_no_owner_does_not_crash(
        self, api_client, community_admin, business
    ):
        business.owner = None
        business.save()
        api_client.force_authenticate(user=community_admin)
        response = api_client.post(
            f"/api/v1/businesses/review/{business.id}/", {"action": "approve"}
        )
        assert response.status_code == 200
        assert (
            Notification.objects.filter(
                notification_type=Notification.BUSINESS_APPROVAL
            ).count()
            == 0
        )


@pytest.mark.django_db
class TestNotificationFKTargets:
    def test_business_approval_notification_has_business_fk(
        self, api_client, community_admin, business
    ):
        api_client.force_authenticate(user=community_admin)
        api_client.post(
            f"/api/v1/businesses/review/{business.id}/", {"action": "approve"}
        )

        notification = Notification.objects.get(
            recipient=business.owner, notification_type=Notification.BUSINESS_APPROVAL
        )
        assert notification.business == business


@pytest.mark.django_db
def test_regrouped_notification_moves_to_top(
    self, api_client, user, other_user, community
):
    from posts.models import Post

    older = Notification.objects.create(
        recipient=user, notification_type=Notification.BUSINESS_APPROVAL, message="Old"
    )

    post = Post.objects.create(
        author=user, community=community, post_type=Post.USER, content="Test"
    )
    like_notification = Notification.objects.create(
        recipient=user,
        notification_type=Notification.LIKE,
        post=post,
        actor=other_user,
        message="Someone liked your post.",
    )

    assert next(iter(Notification.objects.filter(recipient=user))) == like_notification

    older.actor_count += 1
    older.save()

    assert next(iter(Notification.objects.filter(recipient=user))) == older
