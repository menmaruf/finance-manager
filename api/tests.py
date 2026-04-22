import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Category, Transaction, Budget, Goal
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def category(user):
    return Category.objects.create(
        user=user,
        name='Продукты',
        type='expense',
        color='#FF5733'
    )


class TestAuthEndpoints:
    def test_register_user(self, api_client):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'phone': '+79991234567'
        }
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_user(self, api_client, user):
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = api_client.post('/api/auth/login/', data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_get_profile(self, authenticated_client, user):
        response = authenticated_client.get('/api/auth/profile/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username

    def test_update_profile(self, authenticated_client, user):
        data = {'phone': '+79991234567'}
        response = authenticated_client.put('/api/auth/profile/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone'] == '+79991234567'


class TestCategoryEndpoints:
    def test_create_category(self, authenticated_client):
        data = {
            'name': 'Зарплата',
            'type': 'income',
            'color': '#00FF00'
        }
        response = authenticated_client.post('/api/categories/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Зарплата'

    def test_list_categories(self, authenticated_client, category):
        response = authenticated_client.get('/api/categories/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_get_category(self, authenticated_client, category):
        response = authenticated_client.get(f'/api/categories/{category.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == category.name

    def test_update_category(self, authenticated_client, category):
        data = {'name': 'Еда'}
        response = authenticated_client.patch(f'/api/categories/{category.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Еда'

    def test_delete_category(self, authenticated_client, category):
        response = authenticated_client.delete(f'/api/categories/{category.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestTransactionEndpoints:
    def test_create_transaction(self, authenticated_client, category):
        data = {
            'category': category.id,
            'amount': '1500.50',
            'description': 'Покупка продуктов',
            'date': str(date.today())
        }
        response = authenticated_client.post('/api/transactions/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Decimal(response.data['amount']) == Decimal('1500.50')

    def test_list_transactions(self, authenticated_client, category):
        Transaction.objects.create(
            user=authenticated_client.handler._force_user,
            category=category,
            amount=Decimal('1000'),
            date=date.today()
        )
        response = authenticated_client.get('/api/transactions/')
        assert response.status_code == status.HTTP_200_OK

    def test_filter_transactions_by_date(self, authenticated_client, category):
        user = authenticated_client.handler._force_user
        Transaction.objects.create(
            user=user,
            category=category,
            amount=Decimal('1000'),
            date=date.today()
        )
        response = authenticated_client.get(
            f'/api/transactions/?start_date={date.today()}&end_date={date.today()}'
        )
        assert response.status_code == status.HTTP_200_OK


class TestBudgetEndpoints:
    def test_create_budget(self, authenticated_client, category):
        data = {
            'category': category.id,
            'amount': '10000',
            'period': 'monthly',
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=30))
        }
        response = authenticated_client.post('/api/budgets/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_list_budgets(self, authenticated_client):
        response = authenticated_client.get('/api/budgets/')
        assert response.status_code == status.HTTP_200_OK


class TestGoalEndpoints:
    def test_create_goal(self, authenticated_client):
        data = {
            'name': 'Отпуск',
            'target_amount': '100000',
            'current_amount': '0',
            'deadline': str(date.today() + timedelta(days=365))
        }
        response = authenticated_client.post('/api/goals/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Отпуск'

    def test_add_amount_to_goal(self, authenticated_client, user):
        goal = Goal.objects.create(
            user=user,
            name='Машина',
            target_amount=Decimal('500000'),
            current_amount=Decimal('0')
        )
        data = {'amount': '10000'}
        response = authenticated_client.post(f'/api/goals/{goal.id}/add_amount/', data)
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['current_amount']) == Decimal('10000')


class TestAnalyticsEndpoints:
    def test_analytics_summary(self, authenticated_client, category, user):
        Transaction.objects.create(
            user=user,
            category=category,
            amount=Decimal('5000'),
            date=date.today()
        )
        response = authenticated_client.get('/api/analytics/summary/?period=month')
        assert response.status_code == status.HTTP_200_OK
        assert 'income' in response.data
        assert 'expenses' in response.data
        assert 'balance' in response.data

    def test_analytics_by_category(self, authenticated_client):
        response = authenticated_client.get('/api/analytics/by-category/?period=month&type=expense')
        assert response.status_code == status.HTTP_200_OK

    def test_analytics_trends(self, authenticated_client):
        response = authenticated_client.get('/api/analytics/trends/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
