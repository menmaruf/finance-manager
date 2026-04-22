from django.contrib import admin
from .models import User, Category, Transaction, Budget, Goal

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'created_at']
    search_fields = ['username', 'email']
    list_filter = ['created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'color', 'created_at']
    search_fields = ['name', 'user__username']
    list_filter = ['type', 'created_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'date', 'created_at']
    search_fields = ['user__username', 'category__name', 'description']
    list_filter = ['date', 'category__type', 'created_at']
    date_hierarchy = 'date'

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'period', 'start_date', 'end_date']
    search_fields = ['user__username', 'category__name']
    list_filter = ['period', 'start_date']

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'target_amount', 'current_amount', 'is_completed', 'deadline']
    search_fields = ['name', 'user__username']
    list_filter = ['is_completed', 'created_at']
