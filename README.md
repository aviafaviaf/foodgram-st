# Foodgram
Этот проект — часть учебного курса, но он создан полностью самостоятельно.
Цель этого сайта — дать возможность пользователям создавать и хранить рецепты на онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для приготовления блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.

## Как запустить проект
git clone https://github.com/<ваш-юзернейм>/foodgram-project.git
cd foodgram-project

Убедитесь, что установлен Docker и Docker Compose

docker compose up --build

При старте backend автоматически:
выполняет migrate
загружает фикстуры через python manage.py seed_data

Открыть в браузере:
Главная страница: http://localhost
Django admin: http://localhost/admin/

# Данные пользователей:
email: 'admin@example.com', password: 'admin' - админ аккаунт,
email: 'user1@example.com', password: 'pass1234',
email: 'user2@example.com, password: 'pass1234',
email: 'user3@example.com', password: 'pass1234',

## GitHub Actions автоматически:
собирает образы backend и frontend
пушит на Docker Hub
