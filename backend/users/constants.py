from django.core.validators import RegexValidator, EmailValidator

EMAIL_MAX_LENGTH = 254
EMAIL_VALIDATOR = EmailValidator()
EMAIL_VERBOSE_NAME = 'Адрес электронной почты'

USERNAME_MAX_LENGTH = 150
USERNAME_UNIQUE_VALIDATOR = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Разрешены только буквы, цифры и символы . @ + - _'
)
USERNAME_VERBOSE_NAME = 'Уникальный юзернейм'

FIRST_NAME_VERBOSE_NAME = 'Имя'
LAST_NAME_VERBOSE_NAME = 'Фамилия'
NAME_MAX_LENGTH = 150

AVATAR_UPLOAD_PATH = 'users/avatars/'
AVATAR_VERBOSE_NAME = 'Аватар'

SUBSCRIBER_VERBOSE_NAME = 'Подписчик'
AUTHOR_VERBOSE_NAME = 'Автор'
SUBSCRIPTION_VERBOSE_NAME = 'Подписка'
SUBSCRIPTION_VERBOSE_NAME_PLURAL = 'Подписки'
PREVENT_SELF_SUBSCRIPTION_NAME = 'prevent_self_subscription'
UNIQUE_SUBSCRIPTION_NAME = 'unique_subscription'

USER_VERBOSE_NAME = 'Пользователь'
USER_VERBOSE_NAME_PLURAL = 'Пользователи'
USER_ORDERING = ['username']

SUBSCRIPTION_ORDERING = ['author']
