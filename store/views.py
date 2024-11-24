from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category,Product
from .serializers import CategorySerializer,ProductSerializer,ProductCategorySerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from .pagination import CustomPagination

class CategoryAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryUpdateAPIView(APIView):
    permission_classes = [AllowAny]
    def put(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        category.is_active= False
        category.save()

        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)




class ProductAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductUpdateAPIView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete Product
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        product.is_active= True
        product.save()
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)





class ProductListAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        
        category_id = request.query_params.get('category', None)
        
        if category_id:
            products = Product.objects.filter(category_id=category_id,is_active=True)
        else:
            products = Product.objects.all()

        paginator = CustomPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        
        serializer = ProductCategorySerializer(paginated_products, many=True)

        return paginator.get_paginated_response(serializer.data)



class CategoryListAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        
        categories = Category.objects.filter(is_active=True)
        
        serializer = CategorySerializer(categories, many=True)
        
        # Return the serialized data as response
        return Response(serializer.data, status=status.HTTP_200_OK)