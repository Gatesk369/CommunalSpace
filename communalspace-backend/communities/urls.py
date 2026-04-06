from django.urls import path
from .views import (
    CommunityListDetailView,
    CommunityCreateView,
    CommunityUpdateView,
    CommunityDeleteView,
)

urlpatterns = [
    path("communities/", CommunityListDetailView.as_view(), name="community-list"),
    path(
        "communities/<int:pk>/",
        CommunityListDetailView.as_view(),
        name="community-detail",
    ),
    path("create-community/", CommunityCreateView.as_view(), name="community-create"),
    path(
        "update-community/<int:pk>/",
        CommunityUpdateView.as_view(),
        name="community-update",
    ),
    path(
        "delete-community/<int:pk>/",
        CommunityDeleteView.as_view(),
        name="community-delete",
    ),
]
