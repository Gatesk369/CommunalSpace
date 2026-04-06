from django.urls import path
from .views import (
    UserListDetailView,
    UserCreateView,
    UserUpdateView,
    UserDeleteView,
)

urlpatterns = [
    path("users/", UserListDetailView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserListDetailView.as_view(), name="user-detail"),
    path("create-user/", UserCreateView.as_view(), name="user-create"),
    path("update-user/<int:pk>/", UserUpdateView.as_view(), name="user-update"),
    path("delete-user/<int:pk>/", UserDeleteView.as_view(), name="user-delete"),
]
