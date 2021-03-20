from django.contrib import admin
from .models import Category, Transaction

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'category_name', 'is_expense']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'category', 'amount', 'date']
