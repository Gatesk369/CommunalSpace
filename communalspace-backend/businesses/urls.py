from django.urls import path
from .views import (
    BusinessListDetailView,
    BusinessCreateView,
    BusinessUpdateView,
    BusinessDeleteView,
    BusinessApprovalView,
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
    path("pending/", BusinessApprovalView.as_view(), name="business-pending"),
    path("review/<int:pk>/", BusinessApprovalView.as_view(), name="business-review"),
]
