from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from django.db.models import F, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED,)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from djoser.views import UserViewSet as DjoserUserViewSet

from .paginators import LimitPageNumberPagination
from .permissions import (IsAdminOrReadOnly, IsAuthorAdminOrReadOnly,
                          IsAuthorStaffOrReadOnly, UserAndAdminOrReadOnly,)
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
    def subscribe(self, request, id):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED) 
        obj = get_object_or_404(self.queryset, id=id)
        serializer = self.additional_serializer(
            obj, context={'request': self.request}
        )
        obj_exist = user.subscribe.filter(id=id).exists()
        if (self.request.method in ['POST']) and not obj_exist:
            print ('тута')
            user.subscribe.add(obj)
            return Response(serializer.data, status=HTTP_201_CREATED)
        if (self.request.method in ['DELETE']) and obj_exist:
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
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
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

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()
        author = self.request.query_params.get('author')        
        if author:
            queryset = queryset.filter(author=author)
        user = self.request.user
        if user.is_anonymous:
            return queryset
        #print (self.request.query_params)
        is_favorited = self.request.query_params.get('is_favorited')

        print (is_favorited)
        if is_favorited:
            queryset = queryset.filter(favorite=user.id)

        is_in_shopping = self.request.query_params.get('is_in_shopping_cart')

        if is_in_shopping:
            queryset = queryset.filter(cart=user.id)
        return queryset


    @action(methods=('POST', 'DELETE'), detail=True)
    def favorite(self, request, pk):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED) 
        obj = get_object_or_404(self.queryset, id=pk)
        serializer = self.additional_serializer(
            obj, context={'request': self.request}
        )
        obj_exist = user.favorites.filter(id=pk).exists()
        if (self.request.method in ['POST']) and not obj_exist:
            user.favorites.add(obj)
            return Response(serializer.data, status=HTTP_201_CREATED)
        if (self.request.method in ['DELETE']) and obj_exist:
            user.favorites.remove(obj)
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)    

    @action(methods=('POST', 'DELETE'), detail=True)
    def shopping_cart(self, request, pk):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED) 
        obj = get_object_or_404(self.queryset, id=pk)
        serializer = self.additional_serializer(
            obj, context={'request': self.request}
        )
        obj_exist = user.carts.filter(id=pk).exists()
        if (self.request.method in ['POST']) and not obj_exist:
            user.carts.add(obj)
            return Response(serializer.data, status=HTTP_201_CREATED)
        if (self.request.method in ['DELETE']) and obj_exist:
            user.carts.remove(obj)
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)  



    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):

        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = IngredientAmount.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure_unit=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = ("Список покупок\n")
        
        for ingr in ingredients:
            shopping_list += (
                f'{ingr["ingredient"]}: {ingr["amount"]} {ingr["measure_unit"]}\n'
            )
        print (shopping_list)
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response