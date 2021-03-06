# Generated by Django 4.0 on 2022-07-04 18:44

import re

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_email_alter_user_first_name_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientAmount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1, 'Минимальное значение 1'), django.core.validators.MaxValueValidator(1000, 'Максимальное значение 1000')], verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Ингридиент',
                'verbose_name_plural': 'Количество ингридиентов',
                'ordering': ('recipe',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, validators=[django.core.validators.MinLengthValidator(1, 'Введите название')], verbose_name='Тэг')),
                ('color', models.CharField(blank=True, default='FF', max_length=6, null=True, validators=[django.core.validators.MinLengthValidator(6, 'Цветовой HEX-код')], verbose_name='Цветовой HEX-код')),
                ('slug', models.CharField(max_length=150, unique=True, validators=[django.core.validators.MinLengthValidator(3, 'Минимально 3 символа'), django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid')], verbose_name='Слаг тэга')),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
                'ordering': ('name',),
            },
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='unit_of_measurement',
            field=models.CharField(max_length=150, validators=[django.core.validators.MinLengthValidator(1, 'Введите обозначение единицы измерения')], verbose_name='Единицы измерения'),
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название блюда')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('image', models.ImageField(upload_to='recipe_images/', verbose_name='Изображение блюда')),
                ('text', models.TextField(max_length=600, verbose_name='Описание блюда')),
                ('cooking_time', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1, 'Минимальное значение 1 минута'), django.core.validators.MaxValueValidator(300, 'Максимальное значение 300 минут')], verbose_name='Время приготовления')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='users.user', verbose_name='Автор рецепта')),
                ('cart', models.ManyToManyField(related_name='carts', to=settings.AUTH_USER_MODEL, verbose_name='Список покупок')),
                ('favorite', models.ManyToManyField(related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Избранные рецепты')),
                ('ingredients', models.ManyToManyField(related_name='recipes', through='recipes.IngredientAmount', to='recipes.Ingredient', verbose_name='Ингредиенты блюда')),
                ('tags', models.ManyToManyField(related_name='recipes', to='recipes.Tag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.AddField(
            model_name='ingredientamount',
            name='ingredients',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to='recipes.ingredient', verbose_name='Связанные ингредиенты'),
        ),
        migrations.AddField(
            model_name='ingredientamount',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient', to='recipes.recipe', verbose_name='В рецептах'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(fields=('name', 'author'), name='unique_recipe_for_author'),
        ),
        migrations.AddConstraint(
            model_name='ingredientamount',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredients'), name='unique_ingridient_for_recipe'),
        ),
    ]
