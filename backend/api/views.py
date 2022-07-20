from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from django.db.models import F, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import RecipeFilter
from .paginators import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, UserAndAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer, UserSerializer,
                          UserSubscribeSerializer,)
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination
    additional_serializer = UserSubscribeSerializer

    @action(methods=('POST', 'DELETE'), detail=True)
    def subscribe(self, request, **kwargs):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)
        obj = get_object_or_404(self.queryset, id=kwargs.get('id'))
        serializer = self.additional_serializer(
            obj, context={'request': self.request}
        )
        if self.request.method in ['POST']:
            user.subscribe.add(obj)
            return Response(serializer.data, status=HTTP_201_CREATED)
        if self.request.method in ['DELETE']:
            user.subscribe.remove(obj)
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)

    @action(methods=('GET',), detail=False)
    def subscriptions(self, request):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)
        authors = user.subscribe.all()
        pages = self.paginate_queryset(authors)
        serializer = UserSubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    по полю name реализован поиск SearchVector
    не чувствительный к регистру и вхождению в слове
    совместимо только с PostgreSQL
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    # search_fields = ('name',)
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = IngredientFilter
    
    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.annotate(
                search=SearchVector('name'),
            ).filter(search__icontains=name)
        return queryset


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (UserAndAdminOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    additional_serializer = ShortRecipeSerializer
    filter_class = RecipeFilter

    # def get_queryset(self):
    #     queryset = self.queryset
    #     tags = self.request.query_params.getlist('tags')
    #     if tags:
    #         queryset = queryset.filter(
    #             tags__slug__in=tags).distinct()
    #     author = self.request.query_params.get('author')
    #     if author:
    #         queryset = queryset.filter(author=author)
    #     user = self.request.user
    #     if user.is_anonymous:
    #         return queryset
    #     is_favorited = self.request.query_params.get('is_favorited')
    #     if is_favorited:
    #         queryset = queryset.filter(favorite=user.id)
    #     is_in_shopping = self.request.query_params.get('is_in_shopping_cart')
    #     if is_in_shopping:
    #         queryset = queryset.filter(cart=user.id)
    #     return queryset

    def post_delete_obj(self, request, table, **kwargs):
        """
        Вспомогательный метод для добавления/удаления объектов
        user.favorites, user.carts
        """
        user = self.request.user
        pk = kwargs.get('pk')
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)
        obj = get_object_or_404(self.queryset, id=pk)
        serializer = self.additional_serializer(
            obj, context={'request': self.request}
        )
        tables = {
            'favorites':user.favorites,
            'carts':user.carts,
        }
        table = tables[table]
        if self.request.method in ['POST']:
            table.add(obj)
            return Response(serializer.data, status=HTTP_201_CREATED)
        if self.request.method in ['DELETE']:
            table.remove(obj)
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)

    @action(methods=('POST', 'DELETE'), detail=True)
    def favorite(self, request, **kwargs):
        return self.post_delete_obj(request, 'favorites', **kwargs)

    @action(methods=('POST', 'DELETE'), detail=True)
    def shopping_cart(self, request, **kwargs):
        return self.post_delete_obj(request, 'carts', **kwargs)

    @action(methods=('GET',), detail=False)
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = IngredientAmount.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure_unit=F('ingredients__measurement_unit')
        ).annotate(amount_cart=Sum('amount'))
        filename = f'{user.username}_shopping_list.txt'
        shopping_list = ("Список покупок\n")

        for ingr in ingredients:
            shopping_list += (
                f'{ingr["ingredient"]}: '
                f'{ingr["amount_cart"]} '
                f'{ingr["measure_unit"]}\n'
            )
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = (
            f'attachment; filename={filename}.txt'
        )
        return response
