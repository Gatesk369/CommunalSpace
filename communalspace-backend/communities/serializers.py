from rest_framework.serializers import ModelSerializer

from .models import Community, CommunityAdminApplication


class CommunitySerializer(ModelSerializer):
    class Meta:
        model = Community
        fields = "__all__"


class CommunityAdminApplicationSerializer(ModelSerializer):
    class Meta:
        model = CommunityAdminApplication
        fields = [
            "id",
            "applicant",
            "community",
            "status",
            "applied_at",
            "reviewed_at",
            "reviewed_by",
        ]
        read_only_fields = ["status", "applied_at", "reviewed_at", "reviewed_by"]
