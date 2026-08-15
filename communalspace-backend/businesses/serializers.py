from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Business, BusinessBranch, BusinessRating


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
    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

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
            "average_rating",
            "rating_count",
        ]
        read_only_fields = ["owner", "status", "rejection_reason", "created_at"]

    def get_average_rating(self, obj):
        raw = getattr(obj, "avg_stars_raw", None)
        if raw is None:
            return None
        return round(raw / 2, 1)

    def get_rating_count(self, obj):
        return getattr(obj, "rating_count", 0)

    def create(self, validated_data):
        branch_data = validated_data.pop("branch")
        business = Business.objects.create(**validated_data)
        BusinessBranch.objects.create(
            business=business, community=business.community, **branch_data
        )
        return business


class BusinessRatingSerializer(ModelSerializer):
    class Meta:
        model = BusinessRating
        fields = ["id", "business", "user", "stars", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]
