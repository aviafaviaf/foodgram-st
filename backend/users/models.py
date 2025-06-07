from django.contrib.auth.models import AbstractUser
from django.db import models
from .constants import (
    EMAIL_MAX_LENGTH, EMAIL_VALIDATOR, EMAIL_VERBOSE_NAME,
    USERNAME_MAX_LENGTH, USERNAME_UNIQUE_VALIDATOR, USERNAME_VERBOSE_NAME,
    FIRST_NAME_VERBOSE_NAME, LAST_NAME_VERBOSE_NAME, NAME_MAX_LENGTH,
    AVATAR_UPLOAD_PATH, AVATAR_VERBOSE_NAME,
    SUBSCRIBER_VERBOSE_NAME, AUTHOR_VERBOSE_NAME,
    SUBSCRIPTION_VERBOSE_NAME, SUBSCRIPTION_VERBOSE_NAME_PLURAL,
    PREVENT_SELF_SUBSCRIPTION_NAME, UNIQUE_SUBSCRIPTION_NAME,
    USER_VERBOSE_NAME, USER_VERBOSE_NAME_PLURAL, USER_ORDERING,
    SUBSCRIPTION_ORDERING
)


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
        verbose_name=EMAIL_VERBOSE_NAME,
        validators=[EMAIL_VALIDATOR]
    )
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        verbose_name=USERNAME_VERBOSE_NAME,
        validators=[USERNAME_UNIQUE_VALIDATOR]
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name=FIRST_NAME_VERBOSE_NAME
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name=LAST_NAME_VERBOSE_NAME
    )
    avatar = models.ImageField(
        upload_to=AVATAR_UPLOAD_PATH,
        blank=True,
        null=True,
        verbose_name=AVATAR_VERBOSE_NAME
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = USER_VERBOSE_NAME
        verbose_name_plural = USER_VERBOSE_NAME_PLURAL
        ordering = USER_ORDERING

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=SUBSCRIBER_VERBOSE_NAME
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name=AUTHOR_VERBOSE_NAME
    )

    class Meta:
        verbose_name = SUBSCRIPTION_VERBOSE_NAME
        verbose_name_plural = SUBSCRIPTION_VERBOSE_NAME_PLURAL
        ordering = SUBSCRIPTION_ORDERING
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name=UNIQUE_SUBSCRIPTION_NAME
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name=PREVENT_SELF_SUBSCRIPTION_NAME
            )
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
