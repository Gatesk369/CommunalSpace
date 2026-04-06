from rest_framework.serializers import ModelSerializer
from .models import Business


class BusinessSerializer(ModelSerializer):
    class Meta:
        model = Business
        fields = "__all__"
