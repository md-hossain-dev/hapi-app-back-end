from django.contrib import admin
from .models import Category, Product,Transaction,Gift


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Transaction)
admin.site.register(Gift)

