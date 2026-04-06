from django.urls import path
from .views import (
    BusinessListDetailView,
    BusinessCreateView,
    BusinessUpdateView,
    BusinessDeleteView,
)

urlpatterns = [
    path("businesses/", BusinessListDetailView.as_view(), name="business-list"),
    path(
        "businesses/<int:pk>/", BusinessListDetailView.as_view(), name="business-detail"
    ),
    path("create-business/", BusinessCreateView.as_view(), name="business-create"),
    path(
        "update-business/<int:pk>/",
        BusinessUpdateView.as_view(),
        name="business-update",
    ),
    path(
        "delete-business/<int:pk>/",
        BusinessDeleteView.as_view(),
        name="business-delete",
    ),
]
