from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from .models import User, Category, Transaction, Budget, Goal
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    CategorySerializer, TransactionSerializer, BudgetSerializer, GoalSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)

        # Фильтрация по категории
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Фильтрация по дате
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_amount(self, request, pk=None):
        goal = self.get_object()
        amount = request.data.get('amount', 0)

        try:
            amount = float(amount)
            if amount <= 0:
                return Response({'error': 'Сумма должна быть больше нуля'}, status=status.HTTP_400_BAD_REQUEST)

            goal.current_amount += amount
            if goal.current_amount >= goal.target_amount:
                goal.is_completed = True
            goal.save()

            serializer = self.get_serializer(goal)
            return Response(serializer.data)
        except ValueError:
            return Response({'error': 'Неверный формат суммы'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_summary(request):
    user = request.user

    # Получаем параметры периода
    period = request.query_params.get('period', 'month')  # day, week, month, year

    today = datetime.now().date()
    if period == 'day':
        start_date = today
    elif period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=30)

    # Получаем транзакции за период
    transactions = Transaction.objects.filter(user=user, date__gte=start_date, date__lte=today)

    # Считаем доходы и расходы
    income = transactions.filter(category__type='income').aggregate(total=Sum('amount'))['total'] or 0
    expenses = transactions.filter(category__type='expense').aggregate(total=Sum('amount'))['total'] or 0

    return Response({
        'period': period,
        'start_date': start_date,
        'end_date': today,
        'income': income,
        'expenses': expenses,
        'balance': income - expenses,
        'transactions_count': transactions.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_by_category(request):
    user = request.user

    # Получаем параметры
    period = request.query_params.get('period', 'month')
    transaction_type = request.query_params.get('type', 'expense')  # income or expense

    today = datetime.now().date()
    if period == 'day':
        start_date = today
    elif period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=30)

    # Группируем по категориям
    categories = Category.objects.filter(user=user, type=transaction_type)
    result = []

    for category in categories:
        total = Transaction.objects.filter(
            user=user,
            category=category,
            date__gte=start_date,
            date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or 0

        if total > 0:
            result.append({
                'category_id': category.id,
                'category_name': category.name,
                'category_color': category.color,
                'total': total
            })

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_trends(request):
    user = request.user

    # Получаем данные за последние 12 месяцев
    today = datetime.now().date()
    result = []

    for i in range(11, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        if i > 0:
            month_end = (today.replace(day=1) - timedelta(days=(i-1)*30)).replace(day=1) - timedelta(days=1)
        else:
            month_end = today

        income = Transaction.objects.filter(
            user=user,
            category__type='income',
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0

        expenses = Transaction.objects.filter(
            user=user,
            category__type='expense',
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0

        result.append({
            'month': month_start.strftime('%Y-%m'),
            'income': income,
            'expenses': expenses,
            'balance': income - expenses
        })

    return Response(result)
