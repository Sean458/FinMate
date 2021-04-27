from django.contrib import admin
from .models import Category, CustomUser, Transaction, Notification

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'category_name', 'is_expense']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'category',
                    'amount', 'date', 'feedback', 'description']


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'country', 'credit_score']


@admin.register(Notification)
class NotificatioinAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'created_date']
