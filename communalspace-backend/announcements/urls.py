from django.urls import path

from .views import (
    AnnouncementCreateView,
    AnnouncementDeleteView,
    AnnouncementDetailView,
    AnnouncementListView,
    AnnouncementUpdateView,
)

urlpatterns = [
    path("", AnnouncementListView.as_view(), name="announcement-list"),
    path("create/", AnnouncementCreateView.as_view(), name="announcement-create"),
    path("<int:pk>/", AnnouncementDetailView.as_view(), name="announcement-detail"),
    path(
        "<int:pk>/delete/", AnnouncementDeleteView.as_view(), name="announcement-delete"
    ),
    path(
        "<int:pk>/update/", AnnouncementUpdateView.as_view(), name="announcement-update"
    ),
]
