import json

from recipes.models import Ingredient

with open('..//data/ingredients.json', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    Ingredient.objects.get_or_create(
        name=item['name'],
        measurement_unit=item['measurement_unit']
    )

print("Импорт завершен.")
