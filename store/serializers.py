from rest_framework import serializers
from .models import Category,Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']





class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'description','day', 'image', 'price']

    def validate_image(self, value):
        
        if value.size > 2 * 1024 * 1024:  # Limit file size to 2MB
            raise serializers.ValidationError("Image size should not exceed 2MB.")
        return value



class CategoryProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ['id', 'name','category', 'description', 'image', 'price', 'is_active']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['category'] = CategoryProductSerializer(instance.category).data
        return response



