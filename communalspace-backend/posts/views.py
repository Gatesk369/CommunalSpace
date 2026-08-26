from businesses.models import BusinessBranch
from communities.models import Community
from django.db import models
from django.db.models import Count
from django.utils import timezone
from notifications.models import Notification
from rest_framework import status
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, CommentLike, Like, Post, PostMedia, Report
from .serializers import CommentSerializer, PostSerializer, ReportSerializer


# Create your views here.
def get_media_type(file):
    content_type = file.content_type

    if content_type == "image/gif":
        return PostMedia.GIF

    if content_type.startswith("image/"):
        return PostMedia.IMAGE

    if content_type.startswith("video/"):
        return PostMedia.VIDEO

    return None


class PostCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-created_at"


class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        post_type = serializer.validated_data.get("post_type")
        branch = serializer.validated_data.get("branch")

        if post_type == Post.USER:
            if request.user.community is None:
                return Response(
                    {"detail": "You must belong to a community to create a user post."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            post = serializer.save(
                author=request.user,
                community=request.user.community,
            )

        elif post_type == Post.BUSINESS:
            if request.user.role != "business owner":
                return Response(
                    {
                        "detail": "You must be a business owner to create a business post."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if branch is None:
                return Response(
                    {"detail": "You must specify a branch to create a business post."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if branch.business.owner != request.user:
                return Response(
                    {"detail": "You do not own this business branch."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if branch.status != BusinessBranch.APPROVED:
                return Response(
                    {"detail": "This business branch is not approved."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if branch.community is None:
                return Response(
                    {"detail": "This business branch is not assigned to a community."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            post = serializer.save(
                author=request.user,
                community=branch.community,
            )

        else:
            return Response(
                {"detail": "Invalid post type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for file in request.FILES.getlist("media"):
            media_type = get_media_type(file)

            if media_type is None:
                post.delete()
                return Response(
                    {"detail": f"Unsupported media type: {file.name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            PostMedia.objects.create(
                post=post,
                file=file,
                media_type=media_type,
                file_size=file.size,
            )

        return Response(
            PostSerializer(
                post,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class PostBaseView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return (
                Post.objects.select_related("author", "branch", "community")
                .prefetch_related("media")
                .get(pk=pk)
            )
        except Post.DoesNotExist:
            return None


class PostDetailView(PostBaseView):
    def get(self, request, pk):
        post = self.get_object(pk)

        if post is None:
            return Response(
                {"detail": "Post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if post.status != Post.ACTIVE:
            return Response(
                {"detail": "Post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PostSerializer(post, context={"request": request})

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class PostUpdateView(PostBaseView):
    def patch(self, request, pk):
        post = self.get_object(pk)

        if post is None:
            return Response(
                {"detail": "Post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if post.author != request.user:
            return Response(
                {"detail": "You can only edit your own posts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if post.status != Post.ACTIVE:
            return Response(
                {"detail": "This post cannot be edited."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PostSerializer(
            post,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():
            post = serializer.save()

            return Response(
                PostSerializer(
                    post,
                    context={"request": request},
                ).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PostDeleteView(PostBaseView):
    def delete(self, request, pk):
        post = self.get_object(pk)

        if post is None:
            return Response(
                {"detail": "Post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if post.author != request.user:
            return Response(
                {"detail": "You can only delete your own posts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        post.delete()

        return Response(
            {"detail": "Post deleted successfully."},
            status=status.HTTP_200_OK,
        )


class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(
                pk=pk,
                status=Post.ACTIVE,
            )
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        like = Like.objects.filter(
            user=request.user,
            post=post,
        ).first()

        if like:
            like.delete()

            return Response(
                {
                    "detail": "Post unliked.",
                    "liked": False,
                },
                status=status.HTTP_200_OK,
            )

        Like.objects.create(
            user=request.user,
            post=post,
        )

        if post.author and post.author != request.user:
            notification = Notification.objects.filter(
                recipient=post.author,
                notification_type=Notification.LIKE,
                post=post,
                is_read=False,
            ).first()

            if notification:
                notification.actor = request.user
                notification.actor_count += 1
                notification.message = f"{request.user.first_name} and {notification.actor_count - 1} others liked your post."
                notification.save()
            else:
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    notification_type=Notification.LIKE,
                    post=post,
                    message=f"{request.user.first_name} liked your post.",
                )

        return Response(
            {
                "detail": "Post liked.",
                "liked": True,
            },
            status=status.HTTP_201_CREATED,
        )


class PostCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            post = Post.objects.get(
                pk=pk,
                status=Post.ACTIVE,
            )
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        comments = (
            Comment.objects.filter(post=post, is_active=True, parent__isnull=True)
            .select_related("author")
            .annotate(
                like_count=Count("likes", distinct=True),
                reply_count=Count("replies", distinct=True),
            )
            .order_by("created_at")
        )

        serializer = CommentSerializer(
            comments, many=True, context={"request": request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(
                pk=pk,
                status=Post.ACTIVE,
            )
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CommentSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            comment = serializer.save(
                author=request.user,
                post=post,
            )

            if post.author and post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    notification_type=Notification.COMMENT,
                    post=post,
                    comment=comment,
                    message=f'{request.user.first_name} commented: "{comment.content[:100]}"',
                )

            return Response(
                CommentSerializer(comment, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if comment.author != request.user:
            return Response(
                {"detail": "You can only delete your own comments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.delete()

        return Response(
            {"detail": "Comment deleted successfully."},
            status=status.HTTP_200_OK,
        )


class CommentReplyCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            parent = Comment.objects.get(
                pk=pk,
                is_active=True,
                post__status=Post.ACTIVE,
            )
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CommentSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            reply = serializer.save(
                author=request.user,
                post=parent.post,
                parent=parent,
            )

            if parent.author and parent.author != request.user:
                Notification.objects.create(
                    recipient=parent.author,
                    actor=request.user,
                    notification_type=Notification.COMMENT,
                    post=parent.post,
                    comment=reply,
                    message=f'{request.user.first_name} replied to your comment: "{reply.content[:100]}"',
                )

            return Response(
                CommentSerializer(
                    reply,
                    context={"request": request},
                ).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class CommentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            comment = Comment.objects.get(
                pk=pk,
                is_active=True,
                post__status=Post.ACTIVE,
            )
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        like = CommentLike.objects.filter(
            user=request.user,
            comment=comment,
        ).first()

        if like:
            like.delete()

            return Response(
                {
                    "detail": "Comment unliked.",
                    "liked": False,
                },
                status=status.HTTP_200_OK,
            )

        CommentLike.objects.create(
            user=request.user,
            comment=comment,
        )

        return Response(
            {
                "detail": "Comment liked.",
                "liked": True,
            },
            status=status.HTTP_201_CREATED,
        )


class PostListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PostCursorPagination

    def get(self, request):
        posts = (
            Post.objects.filter(status=Post.ACTIVE)
            .select_related("author", "branch", "community")
            .annotate(
                like_count=Count("likes", distinct=True),
                comment_count=Count("comments", distinct=True),
            )
            .prefetch_related("media")
            .order_by("-created_at")
        )

        community_id = request.query_params.get("community")
        post_type = request.query_params.get("post_type")

        if community_id:
            posts = posts.filter(community_id=community_id)

        if post_type:
            posts = posts.filter(post_type=post_type)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(posts, request)

        serializer = PostSerializer(
            page,
            many=True,
            context={"request": request},
        )

        return paginator.get_paginated_response(serializer.data)


class ReportCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReportSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            report = serializer.save(reporter=request.user)

            return Response(
                ReportSerializer(report, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class ReportListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == "admin":
            reports = Report.objects.filter(is_reviewed=False)
        elif user.role == "community admin":
            admin_communities = Community.objects.filter(admins=user)
            reports = Report.objects.filter(
                is_reviewed=False,
            ).filter(
                models.Q(post__community__in=admin_communities)
                | models.Q(comment__post__community__in=admin_communities)
            )
        else:
            return Response(
                {"detail": "You do not have permission to view reports."},
                status=status.HTTP_403_FORBIDDEN,
            )
        reports = reports.select_related(
            "reporter", "post", "comment", "post__community", "comment__post__community"
        ).order_by("created_at")

        serializer = ReportSerializer(reports, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            report = Report.objects.select_related(
                "post", "post__community", "comment", "comment__post__community"
            ).get(pk=pk)
        except Report.DoesNotExist:
            return Response(
                {"detail": "Report not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if report.is_reviewed:
            return Response(
                {"detail": "This report has already been reviewed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_community = (
            report.post.community if report.post else report.comment.post.community
        )

        user = request.user

        if user.role == "admin":
            pass
        elif user.role == "community admin":
            if not Community.objects.filter(
                id=target_community.id, admins=user
            ).exists():
                return Response(
                    {"detail": "You do not administer this community."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            return Response(
                {"detail": "You do not have permission to review reports."},
                status=status.HTTP_403_FORBIDDEN,
            )

        action = request.data.get("action")

        if action not in ("dismiss", "remove"):
            return Response(
                {"detail": "action must be 'dismiss' or 'remove'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == "remove":
            takedown_reason = request.data.get("takedown_reason")
            if not takedown_reason:
                return Response(
                    {"detail": "takedown_reason is required to remove a post."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if report.post:
                report.post.status = Post.REMOVED
                report.post.takedown_reason = takedown_reason
                report.post.save()
                content_author = report.post.author
                content_label = "post"
            else:
                report.comment.is_active = False
                report.comment.takedown_reason = takedown_reason
                report.comment.save()
                content_author = report.comment.author
                content_label = "comment"

            target_filter = (
                {"post": report.post} if report.post else {"comment": report.comment}
            )
            other_reports = Report.objects.filter(
                is_reviewed=False, **target_filter
            ).exclude(pk=report.pk)
            other_reporters = [r.reporter for r in other_reports if r.reporter]
            other_reports.update(is_reviewed=True, reviewed_at=timezone.now())

            if report.reporter:
                Notification.objects.create(
                    recipient=report.reporter,
                    notification_type=Notification.REPORT_OUTCOME,
                    post=report.post,
                    comment=report.comment,
                    message="Your report was reviewed and the content was taken down.",
                )
            for reporter in other_reporters:
                Notification.objects.create(
                    recipient=reporter,
                    notification_type=Notification.REPORT_OUTCOME,
                    post=report.post,
                    comment=report.comment,
                    message="Your report was reviewed and the content was taken down.",
                )
            if content_author:
                Notification.objects.create(
                    recipient=content_author,
                    notification_type=Notification.REPORT_OUTCOME,
                    post=report.post,
                    comment=report.comment,
                    message=f"Your {content_label} was removed. Reason: {takedown_reason}",
                )

        report.is_reviewed = True
        report.reviewed_at = timezone.now()
        report.save()

        return Response(
            ReportSerializer(report, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )
