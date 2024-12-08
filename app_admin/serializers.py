from rest_framework import serializers
from hapi_app.models import User,Country,UserLV
from store.models import Product,Category

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