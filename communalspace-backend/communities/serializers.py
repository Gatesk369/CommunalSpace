from rest_framework.serializers import ModelSerializer
from .models import Community


class CommunitySerializer(ModelSerializer):
    class Meta:
        model = Community
        fields = "__all__"
