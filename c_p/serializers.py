from rest_framework import serializers
from .models import CoupleRelationship, CPLevel, User


class CPLevelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPLevel
        fields = ['id', 'level_name', 'level_up_coins']

    def validate_level_up_coins(self, value):
        if value < 0:
            raise serializers.ValidationError("level up coins cannot be negative.")
        return value



class SimpleInviteSerializer(serializers.Serializer):
    user2_id = serializers.IntegerField()
    cp_level_id = serializers.IntegerField()

