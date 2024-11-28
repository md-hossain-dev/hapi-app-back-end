from rest_framework import serializers
from .models import CreateFamily, FamilyMember, TransactionLog

class CreateFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateFamily
        fields = ['id', 'name', 'family_notification', 'join_mode', 'created_by', 'total_coins', 'created_at', 'level']
        read_only_fields = ['id', 'total_coins', 'created_at', 'created_by']

class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = ['id', 'user', 'family', 'coins_contributed', 'joined_at']
        read_only_fields = ['id', 'joined_at']



class CreateFamilyNEWSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateFamily
        fields = ['id', 'name', 'family_notification', 'join_mode','contribution',  'created_at', 'level']


