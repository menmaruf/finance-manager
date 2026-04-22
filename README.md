# Система управления личными финансами

Курсовая работа по дисциплине "Безопасность программного обеспечения"

## Описание

Backend приложение для управления личными финансами с REST API и современным веб-интерфейсом.

## Функционал

- Регистрация и аутентификация пользователей (JWT)
- Управление категориями доходов и расходов
- Учет транзакций
- Планирование бюджетов
- Постановка финансовых целей
- Аналитика и визуализация данных
- Графики и диаграммы

## Технологии

### Backend
- Python 3.12
- Django 6.0.4
- Django REST Framework 3.17.1
- SQLite
- JWT Authentication

### Frontend
- React 18
- Chart.js
- Axios
- React Router

## Установка и запуск

### Backend

```bash
cd finance_manager
source venv/bin/activate
python manage.py runserver
```

Сервер запустится на http://localhost:8000

### Frontend

```bash
cd frontend
npm start
```

Приложение откроется на http://localhost:3000

## API Endpoints

Всего: 29 endpoints

- Аутентификация: 5 endpoints
- Категории: 5 endpoints
- Транзакции: 5 endpoints
- Бюджеты: 5 endpoints
- Цели: 6 endpoints
- Аналитика: 3 endpoints

Подробное описание в файле ENDPOINTS.md

## Админ панель

URL: http://localhost:8000/admin/
Username: admin
Password: (установить через `python manage.py changepassword admin`)

## Структура проекта

```
finance_manager/
├── backend/              # Django настройки
├── api/                  # API приложение
│   ├── models.py        # Модели данных
│   ├── serializers.py   # Сериализаторы
│   ├── views.py         # Представления
│   └── urls.py          # Маршруты
├── frontend/            # React приложение
│   └── src/
│       ├── components/  # Компоненты
│       └── api.js       # API клиент
└── db.sqlite3          # База данных
```

## Автор

Студент группы 721-1
Томский государственный университет систем управления и радиоэлектроники (ТУСУР)
Кафедра КИБЭВС

## Дата

Апрель 2026
