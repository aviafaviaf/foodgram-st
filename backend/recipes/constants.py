# Максимальные длины
INGREDIENT_NAME_MAX_LENGTH = 100
MEASUREMENT_UNIT_MAX_LENGTH = 50
RECIPE_NAME_MAX_LENGTH = 200

# Путь для загрузки изображений
RECIPE_IMAGE_UPLOAD_PATH = 'recipes/'

# Значения по умолчанию и валидации
AMOUNT_MAX_DIGITS = 6
AMOUNT_DECIMAL_PLACES = 2
MIN_INGREDIENT_AMOUNT = 1
INGREDIENT_AMOUNT_ERROR = 'Количество должно быть не меньше 1.'

# Recipe
RECIPE_VERBOSE_NAME = 'Рецепт'
RECIPE_VERBOSE_NAME_PLURAL = 'Рецепты'
RECIPE_ORDERING = ['-id']
RECIPE_FIELD_AUTHOR = 'Автор'
RECIPE_FIELD_NAME = 'Название рецепта'
RECIPE_FIELD_IMAGE = 'Изображение'
RECIPE_FIELD_TEXT = 'Описание рецепта'
RECIPE_FIELD_COOKING_TIME = 'Время приготовления'
RECIPE_FIELD_INGREDIENTS = 'Ингредиенты'
RECIPE_FIELD_COOKING_TIME_HELP = 'Время приготовления в минутах'

INGREDIENT_VERBOSE_NAME = 'Ингредиент'
INGREDIENT_VERBOSE_NAME_PLURAL = 'Ингредиенты'
INGREDIENT_FIELD_NAME = 'Название ингредиента'
INGREDIENT_FIELD_UNIT = 'Единица измерения'
INGREDIENT_CONSTRAINT_NAME = 'unique_ingredient_unit'

RECIPE_INGREDIENT_VERBOSE_NAME = 'Ингредиент в рецепте'
RECIPE_INGREDIENT_VERBOSE_NAME_PLURAL = 'Ингредиенты в рецептах'
RECIPE_INGREDIENT_FIELD_AMOUNT = 'Количество'
RECIPE_INGREDIENT_CONSTRAINT_NAME = 'unique_recipe_ingredient'

FAVORITE_VERBOSE_NAME = 'Избранное'
FAVORITE_VERBOSE_NAME_PLURAL = 'Избранные рецепты'
FAVORITE_FIELD_USER = 'Пользователь'
FAVORITE_FIELD_RECIPE = 'Рецепт'
FAVORITE_CONSTRAINT_NAME = 'unique_favorite'

CART_VERBOSE_NAME = 'Элемент списка покупок'
CART_VERBOSE_NAME_PLURAL = 'Список покупок'
CART_FIELD_USER = 'Пользователь'
CART_FIELD_RECIPE = 'Рецепт'
CART_CONSTRAINT_NAME = 'unique_cart_item'
