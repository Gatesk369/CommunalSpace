from django.urls import path

from .views import (
    CommentCreateView,
    CommentDeleteView,
    CommentLikeView,
    CommentReplyCreateView,
    PostCommentsView,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostLikeView,
    PostListView,
    PostUpdateView,
)

urlpatterns = [
    path("", PostListView.as_view(), name="post-list"),
    path("create/", PostCreateView.as_view(), name="post-create"),
    path("<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("<int:pk>/update/", PostUpdateView.as_view(), name="post-update"),
    path("<int:pk>/delete/", PostDeleteView.as_view(), name="post-delete"),
    path("<int:pk>/like/", PostLikeView.as_view(), name="post-like"),
    path("<int:pk>/comments/", PostCommentsView.as_view(), name="post-comments"),
    path(
        "<int:pk>/comments/create/", CommentCreateView.as_view(), name="comment-create"
    ),
    path(
        "comments/<int:pk>/delete/", CommentDeleteView.as_view(), name="comment-delete"
    ),
    path(
        "comments/<int:pk>/reply/",
        CommentReplyCreateView.as_view(),
        name="comment-reply",
    ),
    path("comments/<int:pk>/like/", CommentLikeView.as_view(), name="comment-like"),
]
