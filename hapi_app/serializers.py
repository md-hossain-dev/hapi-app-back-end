from rest_framework import serializers
from .models import Image,Wallet,Country,User

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

    
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'



class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','nick_name', 'gender', 'bio', 'country', 'birth_day']


class UserUpdateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','nick_name', 'gender', 'bio', 'country', 'birth_day','profile','first_name','last_name']