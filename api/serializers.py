from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Category, Transaction, Budget, Goal


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email уже используется")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Имя пользователя уже занято")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные учетные данные")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'created_at']
        read_only_fields = ['id', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'icon', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Название категории не может быть пустым")
        if len(name) > 100:
            raise serializers.ValidationError("Название категории слишком длинное")
        return name


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'category', 'category_name', 'category_type', 'amount', 'description', 'date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть больше нуля")
        return value


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    spent_amount = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = ['id', 'category', 'category_name', 'amount', 'period', 'start_date', 'end_date', 'spent_amount', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_spent_amount(self, obj):
        transactions = Transaction.objects.filter(
            user=obj.user,
            category=obj.category,
            date__gte=obj.start_date,
            date__lte=obj.end_date
        )
        return sum(t.amount for t in transactions)

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Дата начала не может быть позже даты окончания")
        return data


class GoalSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Goal
        fields = ['id', 'name', 'target_amount', 'current_amount', 'deadline', 'description', 'is_completed', 'progress_percentage', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'progress_percentage']

    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Целевая сумма должна быть больше нуля")
        return value

    def validate_current_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Текущая сумма не может быть отрицательной")
        return value
