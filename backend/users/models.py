from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, EmailValidator


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Адрес электронной почты',
        validators=[EmailValidator()]
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Уникальный юзернейм',
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Разрешены только буквы, цифры и символы . @ + - _'
        )]
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['author']
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_subscription'),
            models.CheckConstraint(check=~models.Q(user=models.F('author')),
                                   name='prevent_self_subscription')
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
