from rest_framework import serializers
from hapi_app.models import User,Country,UserLV,Wallet
from store.models import Product,Category
from family.models import CreateFamily,BonusLevel,FamilyMember

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password','groups','user_permissions']




class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        exclude = ['short_code','county_flag']


class UserLVListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLV
        exclude = ['created_at']

class StoreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'



class CategoryStoreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'



class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        # Pass the entire `category` instance to the serializer
        response['category'] = CategoryStoreListSerializer(instance.category).data
        return response


class CreatedBySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nick_name']

class CreateFamilyListSerializer(serializers.ModelSerializer):
    total_membar_count = serializers.SerializerMethodField()

    class Meta:
        model = CreateFamily
        fields = '__all__'

    def get_total_membar_count(self, instance):
        return FamilyMember.objects.filter(family=instance).count()

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['created'] = CreatedBySerializer(instance.created_by).data
        return response



class CreateWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','nick_name','email','gender','phone_number','username',]


class UserWalletListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['created'] = CreateWalletSerializer(instance.user).data
        return response





