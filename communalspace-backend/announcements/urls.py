from django.urls import path

from .views import AnnouncementCreateView, AnnouncementDetailView, AnnouncementListView

urlpatterns = [
    path("", AnnouncementListView.as_view(), name="announcement-list"),
    path("create/", AnnouncementCreateView.as_view(), name="announcement-create"),
    path("<int:pk>/", AnnouncementDetailView.as_view(), name="announcement-detail"),
]
