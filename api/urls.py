from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    register, login, profile,
    CategoryViewSet, TransactionViewSet, BudgetViewSet, GoalViewSet,
    analytics_summary, analytics_by_category, analytics_trends
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'goals', GoalViewSet, basename='goal')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/profile/', profile, name='profile'),

    # Analytics endpoints
    path('analytics/summary/', analytics_summary, name='analytics-summary'),
    path('analytics/by-category/', analytics_by_category, name='analytics-by-category'),
    path('analytics/trends/', analytics_trends, name='analytics-trends'),

    # Router endpoints
    path('', include(router.urls)),
]
