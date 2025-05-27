# Foodgram



# Foodgram

**Foodgram** — веб-приложение, предоставляющее пользователям возможность создавать и хранить рецепты на онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для приготовления блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.

---

## Возможности
- Регистрация и авторизация пользователей
- Создание, редактирование и удаление рецептов
- Добавление рецептов в избранное
- Формирование списка покупок
- Просмотр рецептов других пользователей
---

## Как запустить проект локально

### 1. Клонируйте репозиторий:

```bash
git clone https://github.com/aviafaviaf/foodgram-project.git
cd foodgram-project
```

### 2. Убедитесь, что установлены:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### 3. Запустите проект:

```bash
docker compose up --build
```

При старте `backend` автоматически:

- выполняет миграции (`python manage.py migrate`)
- загружает фикстуры (`python manage.py seed_data`)

---

## Доступ к проекту

- Главная страница: [http://localhost](http://localhost)
- Админ-панель Django: [http://localhost/admin/](http://localhost/admin/)

---

## Данные для входа

| Email                  | Пароль    | Роль           |
|------------------------|-----------|----------------|
| admin@example.com      | admin     | Администратор  |
| user1@example.com      | pass1234  | Пользователь 1 |
| user2@example.com      | pass1234  | Пользователь 2 |
| user3@example.com      | pass1234  | Пользователь 3 |

---

## CI/CD

Автоматизация через **GitHub Actions**:

- Сборка образов `backend` и `frontend`
- Публикация на [Docker Hub](https://hub.docker.com/)

---

## Контакты

Разработчик: [aviafaviaf](https://github.com/aviafaviaf)
