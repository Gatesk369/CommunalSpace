from django.urls import path

from .views import (
    CommunityAdminApplicationReviewView,
    CommunityAdminApplicationView,
    CommunityApplicationSeasonView,
    CommunityCreateView,
    CommunityDeleteView,
    CommunityListDetailView,
    CommunityUpdateView,
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
    path(
        "<int:pk>/application-season/",
        CommunityApplicationSeasonView.as_view(),
        name="community-application-season",
    ),
    path(
        "<int:pk>/apply/",
        CommunityAdminApplicationView.as_view(),
        name="community-apply",
    ),
    path(
        "<int:pk>/applications/<int:app_pk>/review/",
        CommunityAdminApplicationReviewView.as_view(),
        name="community-application-review",
    ),
]
