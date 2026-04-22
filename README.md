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


## Админ панель

URL: http://localhost:8000/admin/
Username: admin
Password: (установить через `python manage.py changepassword admin`)

## Структура проекта

```
finance_manager/
├── backend/              # Django настройки
├── api/                  
│   ├── models.py        # Модели данных
│   ├── serializers.py   
│   ├── views.py         
│   └── urls.py          # Маршруты
├── frontend/            
│   └── src/
│       ├── components/  
│       └── api.js       # API клиент
└── db.sqlite3          
```


