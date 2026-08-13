from accounts.models import User
from businesses.models import Business, BusinessBranch
from communities.models import Community
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Comment, CommentLike, Like, Post, Report


class PostAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.community_1 = Community.objects.create(
            name="Community One",
            city="Kampala",
            address="Address One",
        )

        self.community_2 = Community.objects.create(
            name="Community Two",
            city="Kampala",
            address="Address Two",
        )

        self.resident = User.objects.create_user(
            email="resident@example.com",
            password="password123",
            first_name="John",
            last_name="Resident",
            role=User.RESIDENT,
            community=self.community_1,
            is_active=True,
        )

        self.resident_2 = User.objects.create_user(
            email="resident2@example.com",
            password="password123",
            first_name="Jane",
            last_name="Resident",
            role=User.RESIDENT,
            community=self.community_2,
            is_active=True,
        )

        self.business_owner = User.objects.create_user(
            email="business@example.com",
            password="password123",
            first_name="Business",
            last_name="Owner",
            role=User.BUSINESS_OWNER,
            community=self.community_1,
            is_active=True,
        )

        self.non_owner = User.objects.create_user(
            email="notowner@example.com",
            password="password123",
            first_name="Not",
            last_name="Owner",
            role=User.BUSINESS_OWNER,
            community=self.community_1,
            is_active=True,
        )

        self.business = Business.objects.create(
            name="Test Business",
            owner=self.business_owner,
            community=self.community_1,
            status=Business.APPROVED,
        )

        self.branch = BusinessBranch.objects.create(
            business=self.business,
            community=self.community_1,
            address="Branch Address",
            city="Kampala",
            contact_phone="0700000000",
            contact_email="branch@example.com",
            status=BusinessBranch.APPROVED,
        )

        self.post = Post.objects.create(
            author=self.resident,
            community=self.community_1,
            post_type=Post.USER,
            content="Test post",
        )
        self.community_admin = User.objects.create_user(
            email="commadmin@example.com",
            password="password123",
            first_name="Comm",
            last_name="Admin",
            role=User.COMMUNITY_ADMIN,
            community=self.community_1,
            is_active=True,
        )
        self.community_1.admins.add(self.community_admin)

        self.community_admin_2 = User.objects.create_user(
            email="commadmin2@example.com",
            password="password123",
            first_name="Comm2",
            last_name="Admin",
            role=User.COMMUNITY_ADMIN,
            community=self.community_2,
            is_active=True,
        )
        self.community_2.admins.add(self.community_admin_2)

        self.platform_admin = User.objects.create_user(
            email="platformadmin@example.com",
            password="password123",
            first_name="Platform",
            last_name="Admin",
            role=User.ADMIN,
            is_active=True,
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(
            user=user or self.resident,
        )

    # ---------------------------------------------------------
    # POST LIST
    # ---------------------------------------------------------

    def test_post_list_requires_authentication(self):
        response = self.client.get(reverse("post-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_list_returns_active_posts(self):
        self.authenticate()

        Post.objects.create(
            author=self.resident,
            community=self.community_1,
            post_type=Post.USER,
            content="Active post",
            status=Post.ACTIVE,
        )

        Post.objects.create(
            author=self.resident,
            community=self.community_1,
            post_type=Post.USER,
            content="Removed post",
            status=Post.REMOVED,
        )

        response = self.client.get(reverse("post-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_post_list_can_filter_by_community(self):
        self.authenticate()

        Post.objects.create(
            author=self.resident_2,
            community=self.community_2,
            post_type=Post.USER,
            content="Community two post",
        )

        response = self.client.get(
            reverse("post-list"),
            {"community": self.community_2.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["community"],
            self.community_2.id,
        )

    def test_post_list_can_filter_by_post_type(self):
        self.authenticate()

        Post.objects.create(
            author=self.business_owner,
            branch=self.branch,
            community=self.community_1,
            post_type=Post.BUSINESS,
            content="Business post",
        )

        response = self.client.get(
            reverse("post-list"),
            {"post_type": Post.BUSINESS},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["post_type"],
            Post.BUSINESS,
        )

    def test_post_list_can_filter_by_community_and_type(self):
        self.authenticate()

        Post.objects.create(
            author=self.business_owner,
            branch=self.branch,
            community=self.community_1,
            post_type=Post.BUSINESS,
            content="Business post",
        )

        Post.objects.create(
            author=self.business_owner,
            branch=self.branch,
            community=self.community_2,
            post_type=Post.BUSINESS,
            content="Other community business post",
        )

        response = self.client.get(
            reverse("post-list"),
            {
                "community": self.community_1.id,
                "post_type": Post.BUSINESS,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    # ---------------------------------------------------------
    # POST CREATE
    # ---------------------------------------------------------

    def test_resident_can_create_user_post(self):
        self.authenticate()

        response = self.client.post(
            reverse("post-create"),
            {
                "post_type": Post.USER,
                "content": "Hello community!",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        post = Post.objects.get(content="Hello community!")

        self.assertEqual(post.author, self.resident)
        self.assertEqual(post.community, self.community_1)
        self.assertEqual(post.post_type, Post.USER)

    def test_business_owner_can_create_user_post(self):
        self.authenticate(self.business_owner)

        response = self.client.post(
            reverse("post-create"),
            {
                "post_type": Post.USER,
                "content": "Business owner user post",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        post = Post.objects.get(content="Business owner user post")

        self.assertEqual(post.post_type, Post.USER)
        self.assertEqual(post.community, self.community_1)

    def test_business_owner_can_create_business_post(self):
        self.authenticate(self.business_owner)

        response = self.client.post(
            reverse("post-create"),
            {
                "post_type": Post.BUSINESS,
                "branch": self.branch.id,
                "content": "Business announcement",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        post = Post.objects.get(content="Business announcement")

        self.assertEqual(post.author, self.business_owner)
        self.assertEqual(post.branch, self.branch)
        self.assertEqual(post.community, self.branch.community)
        self.assertEqual(post.post_type, Post.BUSINESS)

    def test_resident_cannot_create_business_post(self):
        self.authenticate(self.resident)

        response = self.client.post(
            reverse("post-create"),
            {
                "post_type": Post.BUSINESS,
                "branch": self.branch.id,
                "content": "Unauthorized business post",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_business_owner_cannot_create_business_post_for_someone_elses_branch(
        self,
    ):
        other_business = Business.objects.create(
            name="Other Business",
            owner=self.non_owner,
            community=self.community_1,
            status=Business.APPROVED,
        )

        other_branch = BusinessBranch.objects.create(
            business=other_business,
            community=self.community_1,
            address="Other Address",
            city="Kampala",
            contact_phone="0711111111",
            contact_email="other@example.com",
            status=BusinessBranch.APPROVED,
        )

        self.authenticate(self.business_owner)

        response = self.client.post(
            reverse("post-create"),
            {
                "post_type": Post.BUSINESS,
                "branch": other_branch.id,
                "content": "Someone else's branch",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_business_post_requires_branch(self):
        self.authenticate(self.business_owner)

        response = self.client.post(
            reverse("post-create"),
            {
                "post_type": Post.BUSINESS,
                "content": "No branch",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------
    # POST DETAIL
    # ---------------------------------------------------------

    def test_post_detail(self):
        self.authenticate()

        response = self.client.get(reverse("post-detail", kwargs={"pk": self.post.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.post.id)

    def test_removed_post_is_not_visible(self):
        self.authenticate()

        self.post.status = Post.REMOVED
        self.post.save()

        response = self.client.get(reverse("post-detail", kwargs={"pk": self.post.id}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------------------------------------------------------
    # POST UPDATE
    # ---------------------------------------------------------

    def test_author_can_update_post(self):
        self.authenticate()

        response = self.client.patch(
            reverse("post-update", kwargs={"pk": self.post.id}),
            {"content": "Updated content"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()

        self.assertEqual(self.post.content, "Updated content")

    def test_user_cannot_update_someone_elses_post(self):
        self.authenticate(self.resident_2)

        response = self.client.patch(
            reverse("post-update", kwargs={"pk": self.post.id}),
            {"content": "Hacked content"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------------------------------------------------------
    # POST DELETE
    # ---------------------------------------------------------

    def test_author_can_delete_post(self):
        self.authenticate()

        response = self.client.delete(
            reverse("post-delete", kwargs={"pk": self.post.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_user_cannot_delete_someone_elses_post(self):
        self.authenticate(self.resident_2)

        response = self.client.delete(
            reverse("post-delete", kwargs={"pk": self.post.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------------------------------------------------------
    # POST LIKES
    # ---------------------------------------------------------

    def test_user_can_like_post(self):
        self.authenticate()

        response = self.client.post(reverse("post-like", kwargs={"pk": self.post.id}))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Like.objects.filter(
                user=self.resident,
                post=self.post,
            ).exists()
        )

    def test_user_can_unlike_post(self):
        self.authenticate()

        Like.objects.create(
            user=self.resident,
            post=self.post,
        )

        response = self.client.post(reverse("post-like", kwargs={"pk": self.post.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Like.objects.filter(
                user=self.resident,
                post=self.post,
            ).exists()
        )

    # ---------------------------------------------------------
    # COMMENTS
    # ---------------------------------------------------------

    def test_can_get_post_comments(self):
        self.authenticate()

        Comment.objects.create(
            author=self.resident,
            post=self.post,
            content="Nice post!",
        )

        response = self.client.get(
            reverse("post-comments", kwargs={"pk": self.post.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_can_create_comment(self):
        self.authenticate()

        response = self.client.post(
            reverse("comment-create", kwargs={"pk": self.post.id}),
            {"content": "This is a comment"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Comment.objects.filter(
                author=self.resident,
                post=self.post,
                content="This is a comment",
            ).exists()
        )

    def test_can_delete_own_comment(self):
        self.authenticate()

        comment = Comment.objects.create(
            author=self.resident,
            post=self.post,
            content="Delete me",
        )

        response = self.client.delete(
            reverse("comment-delete", kwargs={"pk": comment.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_cannot_delete_someone_elses_comment(self):
        self.authenticate(self.resident_2)

        comment = Comment.objects.create(
            author=self.resident,
            post=self.post,
            content="Not yours",
        )

        response = self.client.delete(
            reverse("comment-delete", kwargs={"pk": comment.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------------------------------------------------------
    # COMMENT REPLIES
    # ---------------------------------------------------------

    def test_can_reply_to_comment(self):
        self.authenticate()

        comment = Comment.objects.create(
            author=self.resident,
            post=self.post,
            content="Parent comment",
        )

        response = self.client.post(
            reverse("comment-reply", kwargs={"pk": comment.id}),
            {"content": "This is a reply"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        reply = Comment.objects.get(content="This is a reply")

        self.assertEqual(reply.parent, comment)
        self.assertEqual(reply.post, self.post)
        self.assertEqual(reply.author, self.resident)

    def test_comment_list_only_returns_top_level_comments(self):
        self.authenticate()

        parent = Comment.objects.create(
            author=self.resident,
            post=self.post,
            content="Parent",
        )

        Comment.objects.create(
            author=self.resident_2,
            post=self.post,
            parent=parent,
            content="Reply",
        )

        response = self.client.get(
            reverse("post-comments", kwargs={"pk": self.post.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], "Parent")

    # ---------------------------------------------------------
    # COMMENT LIKES
    # ---------------------------------------------------------

    def test_user_can_like_comment(self):
        self.authenticate()

        comment = Comment.objects.create(
            author=self.resident,
            post=self.post,
            content="Like me",
        )

        response = self.client.post(reverse("comment-like", kwargs={"pk": comment.id}))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            CommentLike.objects.filter(
                user=self.resident,
                comment=comment,
            ).exists()
        )

    def test_user_can_unlike_comment(self):
        self.authenticate()

        comment = Comment.objects.create(
            author=self.resident,
            post=self.post,
            content="Unlike me",
        )

        CommentLike.objects.create(
            user=self.resident,
            comment=comment,
        )

        response = self.client.post(reverse("comment-like", kwargs={"pk": comment.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(
            CommentLike.objects.filter(
                user=self.resident,
                comment=comment,
            ).exists()
        )

    # ---------------------------------------------------------
    # REPORT CREATE
    # ---------------------------------------------------------

    def test_report_create_requires_authentication(self):
        response = self.client.post(
            reverse("report-create"),
            {"post": self.post.id, "reason": "spam"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_can_report_a_post(self):
        self.authenticate(self.resident_2)

        response = self.client.post(
            reverse("report-create"),
            {"post": self.post.id, "reason": "spam"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Report.objects.filter(
                reporter=self.resident_2,
                post=self.post,
                reason="spam",
            ).exists()
        )

    def test_can_report_a_comment(self):
        self.authenticate(self.resident_2)

        comment = Comment.objects.create(
            author=self.resident,
            post=self.post,
            content="Reportable comment",
        )

        response = self.client.post(
            reverse("report-create"),
            {"comment": comment.id, "reason": "abuse"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Report.objects.filter(
                reporter=self.resident_2,
                comment=comment,
                reason="abuse",
            ).exists()
        )

    def test_report_requires_post_or_comment(self):
        self.authenticate(self.resident_2)

        response = self.client.post(
            reverse("report-create"),
            {"reason": "spam"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_report_cannot_target_both_post_and_comment(self):
        self.authenticate(self.resident_2)

        comment = Comment.objects.create(
            author=self.resident,
            post=self.post,
            content="Some comment",
        )

        response = self.client.post(
            reverse("report-create"),
            {"post": self.post.id, "comment": comment.id, "reason": "spam"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------
    # REPORT QUEUE
    # ---------------------------------------------------------

    def test_resident_cannot_view_report_queue(self):
        self.authenticate(self.resident)

        response = self.client.get(reverse("report-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_community_admin_sees_only_their_community_reports(self):
        Report.objects.create(
            reporter=self.resident_2, post=self.post, reason=Report.SPAM
        )

        other_post = Post.objects.create(
            author=self.resident_2,
            community=self.community_2,
            post_type=Post.USER,
            content="Other community post",
        )
        Report.objects.create(
            reporter=self.resident, post=other_post, reason=Report.ABUSE
        )

        self.authenticate(self.community_admin)

        response = self.client.get(reverse("report-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["post"], self.post.id)

    def test_platform_admin_sees_all_reports(self):
        Report.objects.create(
            reporter=self.resident_2, post=self.post, reason=Report.SPAM
        )

        other_post = Post.objects.create(
            author=self.resident_2,
            community=self.community_2,
            post_type=Post.USER,
            content="Other community post",
        )
        Report.objects.create(
            reporter=self.resident, post=other_post, reason=Report.ABUSE
        )

        self.authenticate(self.platform_admin)

        response = self.client.get(reverse("report-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_report_queue_excludes_reviewed_reports(self):
        Report.objects.create(
            reporter=self.resident_2,
            post=self.post,
            reason=Report.SPAM,
            is_reviewed=True,
        )

        self.authenticate(self.community_admin)

        response = self.client.get(reverse("report-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ---------------------------------------------------------
    # REPORT REVIEW
    # ---------------------------------------------------------

    def test_community_admin_can_dismiss_report(self):
        report = Report.objects.create(
            reporter=self.resident_2, post=self.post, reason=Report.SPAM
        )

        self.authenticate(self.community_admin)

        response = self.client.patch(
            reverse("report-review", kwargs={"pk": report.id}),
            {"action": "dismiss"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        report.refresh_from_db()
        self.post.refresh_from_db()

        self.assertTrue(report.is_reviewed)
        self.assertIsNotNone(report.reviewed_at)
        self.assertEqual(self.post.status, Post.ACTIVE)

    def test_community_admin_can_remove_reported_post(self):
        report = Report.objects.create(
            reporter=self.resident_2, post=self.post, reason=Report.SPAM
        )

        self.authenticate(self.community_admin)

        response = self.client.patch(
            reverse("report-review", kwargs={"pk": report.id}),
            {"action": "remove", "takedown_reason": "Violates community guidelines"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        report.refresh_from_db()
        self.post.refresh_from_db()

        self.assertTrue(report.is_reviewed)
        self.assertEqual(self.post.status, Post.REMOVED)
        self.assertEqual(self.post.takedown_reason, "Violates community guidelines")

    def test_remove_action_requires_takedown_reason(self):
        report = Report.objects.create(
            reporter=self.resident_2, post=self.post, reason=Report.SPAM
        )

        self.authenticate(self.community_admin)

        response = self.client.patch(
            reverse("report-review", kwargs={"pk": report.id}),
            {"action": "remove"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        report.refresh_from_db()
        self.assertFalse(report.is_reviewed)

    def test_community_admin_can_remove_reported_comment(self):
        comment = Comment.objects.create(
            author=self.resident, post=self.post, content="Bad comment"
        )
        report = Report.objects.create(
            reporter=self.resident_2, comment=comment, reason=Report.ABUSE
        )

        self.authenticate(self.community_admin)

        response = self.client.patch(
            reverse("report-review", kwargs={"pk": report.id}),
            {"action": "remove", "takedown_reason": "Abusive language"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        report.refresh_from_db()
        comment.refresh_from_db()

        self.assertTrue(report.is_reviewed)
        self.assertFalse(comment.is_active)
        self.assertEqual(comment.takedown_reason, "Abusive language")

    def test_community_admin_cannot_review_report_outside_their_community(self):
        report = Report.objects.create(
            reporter=self.resident_2, post=self.post, reason=Report.SPAM
        )

        self.authenticate(self.community_admin_2)

        response = self.client.patch(
            reverse("report-review", kwargs={"pk": report.id}),
            {"action": "dismiss"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        report.refresh_from_db()
        self.assertFalse(report.is_reviewed)

    def test_resident_cannot_review_reports(self):
        report = Report.objects.create(
            reporter=self.resident_2, post=self.post, reason=Report.SPAM
        )

        self.authenticate(self.resident)

        response = self.client.patch(
            reverse("report-review", kwargs={"pk": report.id}),
            {"action": "dismiss"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_review_already_reviewed_report(self):
        report = Report.objects.create(
            reporter=self.resident_2,
            post=self.post,
            reason=Report.SPAM,
            is_reviewed=True,
        )

        self.authenticate(self.community_admin)

        response = self.client.patch(
            reverse("report-review", kwargs={"pk": report.id}),
            {"action": "dismiss"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_action_rejected(self):
        report = Report.objects.create(
            reporter=self.resident_2, post=self.post, reason=Report.SPAM
        )

        self.authenticate(self.community_admin)

        response = self.client.patch(
            reverse("report-review", kwargs={"pk": report.id}),
            {"action": "banish_to_the_shadow_realm"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        report.refresh_from_db()
        self.assertFalse(report.is_reviewed)

    def test_platform_admin_can_review_any_community_report(self):
        other_post = Post.objects.create(
            author=self.resident_2,
            community=self.community_2,
            post_type=Post.USER,
            content="Other community post",
        )
        report = Report.objects.create(
            reporter=self.resident, post=other_post, reason=Report.MISINFO
        )

        self.authenticate(self.platform_admin)

        response = self.client.patch(
            reverse("report-review", kwargs={"pk": report.id}),
            {"action": "remove", "takedown_reason": "False information"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        other_post.refresh_from_db()
        self.assertEqual(other_post.status, Post.REMOVED)
