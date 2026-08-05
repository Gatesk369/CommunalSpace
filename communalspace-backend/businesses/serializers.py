from rest_framework.serializers import ModelSerializer

from .models import Business, BusinessBranch


class BusinessBranchSerializer(ModelSerializer):
    class Meta:
        model = BusinessBranch
        fields = [
            "id",
            "address",
            "city",
            "contact_phone",
            "contact_email",
            "status",
            "rejection_reason",
        ]
        read_only_fields = ["status", "rejection_reason"]


class BusinessSerializer(ModelSerializer):
    branch = BusinessBranchSerializer(write_only=True)

    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "owner",
            "community",
            "status",
            "rejection_reason",
            "created_at",
            "branch",
        ]
        read_only_fields = ["owner", "status", "rejection_reason", "created_at"]

    def create(self, validated_data):
        branch_data = validated_data.pop("branch")
        business = Business.objects.create(**validated_data)
        BusinessBranch.objects.create(
            business=business, community=business.community, **branch_data
        )
        return business
