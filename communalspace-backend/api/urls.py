from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpaceViewSet

router = DefaultRouter()
router.register(r"spaces", SpaceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
