from rest_framework import serializers
from .models import Space

class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = ['id', 'name', 'description', 'location_type', 'date_added']