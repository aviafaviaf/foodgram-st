import os
import json
from io import BytesIO
from PIL import Image

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from recipes.models import Ingredient, Recipe, RecipeIngredient


class Command(BaseCommand):
    help = 'Seed database with ingredients, users, and sample recipes'

    def generate_image(self):
        file = BytesIO()
        image = Image.new('RGB', (300, 300), color='grey')
        image.save(file, 'png')
        return ContentFile(file.getvalue(), 'test.png')

    def handle(self, *args, **kwargs):
        if Recipe.objects.exists():
            self.stdout.write(
                self.style.WARNING('Данные уже созданы. Пропускаем.'))
            return

        BASE_DIR = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        json_path = os.path.join(BASE_DIR, 'data', 'ingredients.json')

        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        ingredients = [
            Ingredient(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
            for item in data
        ]

        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Ингредиенты загружены.'))

        User = get_user_model()

        admin_email = 'admin@example.com'
        admin_username = 'admin'
        admin_password = 'admin'

        admin_user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'username': admin_username,
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )

        if created:
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(
                f'Админ-пользователь создан: {admin_email} / {admin_password}'
            ))

        users_data = [
            {'username': 'user1', 'email': 'user1@example.com',
             'password': 'pass1234'},
            {'username': 'user2', 'email': 'user2@example.com',
             'password': 'pass1234'},
            {'username': 'user3', 'email': 'user3@example.com',
             'password': 'pass1234'},
        ]
        new_users = []

        for data in users_data:
            user = User(
                username=data['username'],
                email=data['email'],
                first_name=data['username'].capitalize(),
                last_name='Testov'
            )
            user.set_password(data['password'])
            new_users.append(user)

        User.objects.bulk_create(new_users)
        self.stdout.write(self.style.SUCCESS('Пользователи созданы.'))

        recipes_data = [
            {'name': 'Борщ', 'text': 'Свекольный суп', 'cooking_time': 60},
            {'name': 'Паста', 'text': 'С сыром и соусом', 'cooking_time': 30},
            {'name': 'Омлет', 'text': 'Быстрый завтрак', 'cooking_time': 10},
        ]

        ingredients = list(Ingredient.objects.all()[:3])
        recipes = []

        for i, user in enumerate(new_users):
            r_data = recipes_data[i]
            recipe = Recipe.objects.create(
                author=user,
                name=r_data['name'],
                text=r_data['text'],
                cooking_time=r_data['cooking_time'],
            )
            recipe.image.save(f"{recipe.name}.png", self.generate_image(),
                              save=True)
            recipes.append(recipe)

        bulk_links = []
        for i, recipe in enumerate(recipes):
            for ingredient in ingredients:
                bulk_links.append(RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=1
                ))

        RecipeIngredient.objects.bulk_create(bulk_links)
        self.stdout.write(
            self.style.SUCCESS('Рецепты созданы и заполнены ингредиентами.'))
