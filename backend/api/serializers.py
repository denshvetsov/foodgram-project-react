from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import F

from drf_extra_fields.fields import Base64ImageField

from rest_framework.serializers import (ModelSerializer, SerializerMethodField,
                                        ValidationError,)

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag

User = get_user_model()


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, username):
        if (
            settings.MAX_LEN_USER_CHARFIELD
            < len(username)
            < settings.MAX_LEN_USER_CHARFIELD
        ):
            raise ValidationError(
                f'Длина допустима от '
                f'{settings.MIN_LEN_USER_CHARFIELD}'
                f'до {settings.MAX_LEN_USER_CHARFIELD}'
            )
        if not username.isalpha():
            raise ValidationError(
                'Допустимы только буквы.'
            )
        return username.lower()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscribe.filter(id=obj.id).exists()


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',


class UserSubscribeSerializer(UserSerializer):
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_is_subscribed(*args):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.carts.filter(id=obj.id).exists()

    def validate(self, data):
        name = self.initial_data.get('name')
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        # преобразуем id ингридиентов в объекты связанной таблицы
        validated_ingredients = []
        for ingr in ingredients:
            ingr_id = ingr.get('id')
            # преобразуем queryset в один объект
            ingredient = Ingredient.objects.filter(id=ingr_id)[0]
            amount = ingr.get('amount')
            validated_ingredients.append(
                {'ingredient': ingredient, 'amount': amount}
            )
        # переопределим выходные данные
        data['name'] = name
        data['tags'] = tags
        data['ingredients'] = validated_ingredients
        data['author'] = self.context.get('request').user
        return data

    def create(self, validated_data):
        """
        Cоздание рецепта
        endpoint: /api/recipes/create/
        на входе: проверенные и преобразованные данные def validate
        логика работы:
            1. готовим данные для записи
            - определяем временные переменные image, ingredients, tags.
            и удаляем их из сериализатора
            2. записываем в таблицы
            - создаем запись recipe, отдельно передаем image
            - обновляем поле recipe.tags
            - пишем IngredientAmount, используем преобразованные
            в validate data['ingredients']
        """
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientAmount.objects.get_or_create(
                recipe=recipe,
                ingredients=ingredient['ingredient'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        recipe.image = validated_data.get(
            'image', recipe.image)
        recipe.name = validated_data.get(
            'name', recipe.name)
        recipe.text = validated_data.get(
            'text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time)
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            for ingredient in ingredients:
                IngredientAmount.objects.get_or_create(
                    recipe=recipe,
                    ingredients=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
        recipe.save()
        return recipe