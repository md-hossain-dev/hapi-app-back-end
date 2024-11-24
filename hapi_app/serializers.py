from rest_framework import serializers
from .models import Image,Wallet

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image','user','uploaded_at'] 



class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'gold_coins']

    def validate_gold_coins(self, value):
        if value < 0:
            raise serializers.ValidationError("Gold coins cannot be negative.")
        return value

    
