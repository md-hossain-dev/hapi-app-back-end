from django.urls import path
from .views import CategoryAPIView,CategoryUpdateAPIView,CategoryListAPIView,ProductAPIView,ProductUpdateAPIView,ProductListAPIView

urlpatterns = [
    path('categories-create/', CategoryAPIView.as_view(), name='create-category'),
    path('categories/<int:pk>/', CategoryUpdateAPIView.as_view(), name='update-delete-category'),
    path('products-create/', ProductAPIView.as_view(), name='create-product'),
    path('products/<int:pk>/', ProductUpdateAPIView.as_view(), name='update-delete-product'),
    path('categories-with-products/', ProductListAPIView.as_view(), name='categories-with-products'),
    path('category-list/', CategoryListAPIView.as_view(), name='category-list'),
]



