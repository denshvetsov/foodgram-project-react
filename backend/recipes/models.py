from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator, RegexValidator,
                                    validate_slug,)
from django.db.models import (CASCADE, CharField, DateTimeField, ForeignKey,
                              ImageField, ManyToManyField, Model,
                              PositiveSmallIntegerField, TextField,
                              UniqueConstraint,)
from django.utils.html import format_html
from django.utils.safestring import mark_safe

User = get_user_model()


class Ingredient(Model):
    """
    Модель интгридиентов - ингридиенты добавляются администратором
    через admin панель. Обязательная проверка на уникальность
    сочетания name и measurement_unit
    search_vector - вспомогательное поле для поиска ингридиента
    """
    name = CharField(
        verbose_name='Ингридиент',
        max_length=settings.MAX_LEN_INGRIDIENT_CHARFIELD,
        validators=[
            MinLengthValidator(
                settings.MIN_LEN_INGRIDIENT_CHARFIELD,
                settings.MIN_LEN_INGRIDIENT_ERROR_MSG
            )
        ]
    )
    measurement_unit = CharField(
        verbose_name='Единицы измерения',
        max_length=settings.MAX_LEN_INGRIDIENT_CHARFIELD,
        validators=[
            MinLengthValidator(
                1, 'Введите обозначение единицы измерения'
            )
        ]
    )
    search_vector = SearchVectorField(null=True)

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name', )
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='ingredient_with_unit'
            ),
        )

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Tag(Model):
    """
    Тег используется для фильтра рецептов. Создает администратор
    через admin панель
    color - цветовой код в формате #F08080
    """

    name = CharField(
        verbose_name='Тэг',
        max_length=settings.MAX_LEN_RECIPE_CHARFIELD,
        unique=True,
        validators=[
            MinLengthValidator(1, 'Введите название'),
        ]
    )
    color = CharField(
        verbose_name='Цветовой HEX-код',
        max_length=7,
        blank=True,
        null=True,
        default='#',
        unique=True,
        validators=[
            RegexValidator(
                "^#([A-Fa-f0-9]{6})$",
                "введите код цвета в формате #F08080"
            ),
        ],
    )
    slug = CharField(
        verbose_name='Слаг тэга',
        max_length=settings.MAX_LEN_RECIPE_CHARFIELD,
        unique=True,
        validators=[
            MinLengthValidator(3, 'Минимально 3 символа'),
            validate_slug,
        ]
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name', )

    @admin.display
    def color_code(self):
        """
        отображение цвета тега в админ панели
        """
        return mark_safe(
            format_html(
                '<span style="color: {};">{}</span>',
                self.color,
                self.color,
            )
        )

    def save(self, *args, **kwargs):
        """
        превод слега в нижний регистр при сохранении
        """
        self.slug = self.slug.lower()
        return super(Tag, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Recipe(Model):
    name = CharField(
        verbose_name='Название блюда',
        max_length=settings.MAX_LEN_RECIPE_CHARFIELD,
        validators=(
            MinLengthValidator(
                settings.MIN_LEN_RECIPE_CHARFIELD,
                settings.MIN_LEN_USER_ERROR_MSG
            ),
            RegexValidator(
                '^[a-zA-Zа-яА-Я ]+$',
                (
                    'Название может быть только из русских, '
                    'латниских букв и пробела между словами'
                )
            )
        )
    )
    author = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='recipes',
        to=User,
        on_delete=CASCADE,
    )
    favorite = ManyToManyField(
        verbose_name='Избранные рецепты',
        related_name='favorites',
        to=User,
    )
    tags = ManyToManyField(
        verbose_name='Теги',
        related_name='recipes',
        to='Tag',
    )
    ingredients = ManyToManyField(
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
        to=Ingredient,
        through='recipes.IngredientAmount',
    )
    cart = ManyToManyField(
        verbose_name='Список покупок',
        related_name='carts',
        to=User,
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    image = ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipe_images/',
    )
    text = TextField(
        verbose_name='Описание блюда',
        max_length=settings.MAX_LEN_RECIPE_TEXTFIELD,
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=(
            MinValueValidator(
                1,
                'Минимальное значение 1 минута'
            ),
            MaxValueValidator(
                300,
                'Максимальное значение 300 минут'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )
        constraints = (
            UniqueConstraint(
                fields=('name', 'author'),
                name='unique_recipe_for_author'
            ),
        )

    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author.username}'


class IngredientAmount(Model):
    """
    количество ингридиента в рецептах
    каждый ингридиент в рецепте используется только один раз
    """
    recipe = ForeignKey(
        verbose_name='В рецептах',
        related_name='ingredient',
        to=Recipe,
        on_delete=CASCADE,
    )
    ingredients = ForeignKey(
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        to=Ingredient,
        on_delete=CASCADE,
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(
            MinValueValidator(
                1, 'Минимальное значение 1'
            ),
            MaxValueValidator(
                1000, 'Максимальное значение 1000'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipe', )
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'ingredients', ),
                name='unique_ingridient_for_recipe',
            ),
        )

    def __str__(self) -> str:
        return f'{self.ingredients}'
