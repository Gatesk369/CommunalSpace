from rest_framework import serializers

from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "content",
            "urgency",
            "communities",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_communities(self, value):
        if not value:
            raise serializers.ValidationError(
                "An announcement must be tied to at least one community."
            )
        return value
