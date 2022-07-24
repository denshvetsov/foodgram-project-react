from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models import CharField, EmailField, ManyToManyField

USER = 'user'
ADMIN = 'admin'


class User(AbstractUser):
    """
    Модель пользователя.
    role - роль пользователя, назначается через админ панель
    по умолчанию присваивается USER
    AMDIN - дает права изменять рецепты созданные другими пользователями
    email - электронная почта, используется при авторизации
    """

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
                settings.MIN_LEN_USER_CHARFIELD,
                settings.MIN_LEN_USER_ERROR_MSG
            ),
            RegexValidator(
                '^[a-zA-Zа-яА-Я@.]+$',
                ('"Имя пользователя" может содержать русские'
                 'латинские символы, знак ".", знак "@"')
            )
        )
    )
    first_name = CharField(
        verbose_name='Имя',
        max_length=settings.MAX_LEN_USER_CHARFIELD,
        validators=(
            MinLengthValidator(
                settings.MIN_LEN_USER_CHARFIELD,
                settings.MIN_LEN_USER_ERROR_MSG
            ),
            RegexValidator(
                '^[a-zA-Zа-яА-Я@.]+$',
                ('"Имя" может содержать русские'
                 'латинские символы, знак ".", знак "@"')
            )
        )
    )
    last_name = CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_LEN_USER_CHARFIELD,
        validators=(
            MinLengthValidator(
                settings.MIN_LEN_USER_CHARFIELD,
                settings.MIN_LEN_USER_ERROR_MSG
            ),
            RegexValidator(
                '^[a-zA-Zа-яА-Я@.]+$',
                ('"Фамилия"  может содержать русские'
                 'латинские символы, знак ".", знак "@"')
            )
        )
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
