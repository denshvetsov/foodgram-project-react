from django.conf import settings
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    CharField, IntegerField, ModelSerializer, PrimaryKeyRelatedField,
    SerializerMethodField, ValidationError,)
from rest_framework.validators import UniqueTogetherValidator

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
                f'В поле username длина допустима от '
                f'{settings.MIN_LEN_USER_CHARFIELD}'
                f'до {settings.MAX_LEN_USER_CHARFIELD}'
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
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        query_params = self.context['request'].query_params
        recipes_limit = query_params.get('recipes_limit', False)
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        else:
            recipes = Recipe.objects.filter(author=obj)
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data


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


class IngredientInRecipeSerializer(ModelSerializer):
    id = IntegerField(source="ingredients.id")
    name = CharField(source="ingredients.name", read_only=True)
    measurement_unit = CharField(
        source="ingredients.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientAmount
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )
        read_only_fields = ("name", "measurement_unit")
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientAmount.objects.all(),
                fields=['ingredients', 'recipe']
            )
        ]


class IngredientRecipeCreateSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True, source='ingredient_amount', read_only=True
    )
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


class RecipeCreateSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
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
        """Логика работы:
        - поля name, text, cooking_time
        уже валидированы на уровне модели и доступны в data,
        мы их сохраним автоматом при обновлении или создания рецепта.
        - поле tags - значения валидируется на уровне модели,
        убедимся в наличии минимум 1 тега
        - ingredients валидируем наличие в рецепте и количество
        """
        tags = data.get('tags')
        ingredients = data.get('ingredients')
        if not tags:
            raise ValidationError(
                'Необходим минимум один тег'
            )
        if not ingredients:
            raise ValidationError(
                {'ingredients': 'В рецепте нужны ингредиенты'}
            )
        validated_ingredients_obj = []
        for ingredient_item in ingredients:
            ingr_obj = ingredient_item['id']
            if ingr_obj in validated_ingredients_obj:
                raise ValidationError(
                    f'"{ingr_obj}" уже добавлен в рецепт'
                )
            amount = ingredient_item.get('amount')
            if type(amount) is not int or (amount < 1 or amount > 10000):
                raise ValidationError(
                    (f'Некорректное количество "{amount}" '
                     f'ингредиента "{ingr_obj}". Допустимы только '
                      'целые цифровые значения больше 1 и меньше 10000')
                )
            validated_ingredients_obj.append(ingr_obj)
        return data

    def validate_cooking_time(self, data):
        if data <= 0 or data > 300:
            raise ValidationError(
                'Время приготовления не должно быть '
                ' больше 0 и меньше 300 минут.'
            )
        return data

    def validate_name(self, data):
        """
        Пост процессинг названия рецепта для корректной
        работы UniqueConstraint. Удаляем двойные пробелы,
        пробелы вначале и в конце предложения.
        переводим имя в нижний регистр
        """
        name = " ".join(data.split()).strip().lower()
        return name

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientAmount.objects.get_or_create(
                recipe=recipe,
                ingredients=ingredient['id'],
                amount=ingredient['amount']
            )

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
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Логика работы:
        - Поля по умолчанию обновляются
          super().update(instance, validated_data)
        - ingredients
          self.create_ingredients(ingredients, instance)
        - tags
          instance.tags.set(tags)
        """
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.clear()
            instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
        return data
