from rest_framework.serializers import ModelSerializer

from .models import Community, CommunityAdminApplication


class CommunitySerializer(ModelSerializer):
    class Meta:
        model = Community
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["admin_names"] = [
            {"id": admin.id, "name": f"{admin.first_name} {admin.last_name}"}
            for admin in instance.admins.all()
        ]
        return data


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
