from rest_framework import serializers
from .models import MedalInfo,UserMedal

class MedalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedalInfo
        fields = '__all__'



class UserMedalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMedal
        fields = '__all__'
