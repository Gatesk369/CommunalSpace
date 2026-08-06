from django.urls import path

from .views import (
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserChangePasswordView,
    UserCreateView,
    UserDeleteView,
    UserListDetailView,
    UserUpdateView,
    UserVerifyEmailView,
)

urlpatterns = [
    path("users/", UserListDetailView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserListDetailView.as_view(), name="user-detail"),
    path("create-user/", UserCreateView.as_view(), name="user-create"),
    path("update-user/<int:pk>/", UserUpdateView.as_view(), name="user-update"),
    path("delete-user/<int:pk>/", UserDeleteView.as_view(), name="user-delete"),
    path("change-password/", UserChangePasswordView.as_view(), name="change-password"),
    path(
        "verify-email/<uuid:token>/", UserVerifyEmailView.as_view(), name="verify-email"
    ),
    path(
        "reset-password/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "reset-password/<uuid:token>/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
