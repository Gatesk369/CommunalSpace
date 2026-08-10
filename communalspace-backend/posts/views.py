from businesses.models import BusinessBranch
from django.db.models import Count
from rest_framework import status
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, CommentLike, Like, Post, PostMedia
from .serializers import CommentSerializer, PostSerializer


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
