import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models import (CASCADE, CharField, CheckConstraint, EmailField,
                              F, ForeignKey, ManyToManyField, Model, Q,
                              UniqueConstraint,)

USER = 'user'
ADMIN = 'admin'

class User(AbstractUser):
    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )
    role = CharField(
        'Роль', max_length=9, choices=ROLE_CHOICES, default=USER,
        error_messages={'validators': 'Выбрана несуществующая роль'}
    )
    email = EmailField(
        verbose_name='Адрес электронной почты',
        max_length=settings.MAX_LEN_EMAIL_CHARFIELD,
        unique=True,
    )
    username = CharField(
        verbose_name='Уникальное имя пользователя',
        max_length=settings.MAX_LEN_USER_CHARFIELD,
        unique=True,
        validators=(
            MinLengthValidator(
                settings.MIN_LEN_INGRIDIENT_CHARFIELD, settings.MIN_LEN_USER_ERROR_MSG
            ),
            RegexValidator(
                '^[a-zA-Zа-яА-Я]+$'
            )
        )
    )
    first_name = CharField(
        verbose_name='Имя',
        max_length=settings.MAX_LEN_USER_CHARFIELD,
    )
    last_name = CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_LEN_USER_CHARFIELD,
    )

    subscribe = ManyToManyField(
        verbose_name='Подписка на других пользователей',
        related_name='subscribers',
        to='self',
        symmetrical=False,
        blank=True
    )
    
    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    def __str__(self):
        return f'{self.username}: {self.email}'
