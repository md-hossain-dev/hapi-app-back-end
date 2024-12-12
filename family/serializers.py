from rest_framework import serializers
from .models import CreateFamily, FamilyMember, TransactionLog
from hapi_app.models import UserLV,User

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
        fields = ['id', 'name', 'family_notification', 'join_mode','contribution','family_image',  'created_at', 'level']


class UserLVAPPListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLV
        exclude = ['created_at']



class FamilyMemberUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nick_name', 'profile']


class FamilyMemberAllSerializer(serializers.ModelSerializer):
    user = FamilyMemberUserSerializer() 
    family = serializers.SerializerMethodField()
    total_membar_count = serializers.SerializerMethodField()

    class Meta:
        model = FamilyMember
        fields = ['id', 'user', 'family', 'coins_contributed', 'joined_at', 'is_join', 'contribution', 'is_leader', 'reward', 'total_membar_count']

    def get_family(self, instance):
        return {
            "id": instance.family.id,
            "name": instance.family.name,
            "family_image": instance.family.family_image.url if instance.family.family_image else None,
        }

    def get_total_membar_count(self, instance):
        return FamilyMember.objects.filter(family=instance.family).count()







class CreateFamilyListWithMembarSerializer(serializers.ModelSerializer):
    total_membar_count = serializers.SerializerMethodField()

    class Meta:
        model = CreateFamily
        fields = ['id', 'name', 'family_notification', 'join_mode', 'contribution', 'family_image', 
                  'created_at', 'level', 'total_membar_count']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['f_membar'] = FamilyMemberAllMembarSerializer(
            FamilyMember.objects.filter(family=instance).order_by('-contribution'), many=True).data
        return response

    def get_total_membar_count(self, instance):
        return FamilyMember.objects.filter(family=instance).count()


class FamilyMemberAllMembarSerializer(serializers.ModelSerializer):
    user = FamilyMemberUserSerializer() 

    class Meta:
        model = FamilyMember
        fields = ['id', 'user', 'family', 'coins_contributed', 'joined_at', 'is_join', 
                  'contribution', 'is_leader', 'reward']


