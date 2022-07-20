# from django_filters.rest_framework import FilterSet, filters
# from django.contrib.postgres.search import SearchVector
# from rest_framework.filters import BaseFilterBackend

from crypt import methods
from recipes.models import Ingredient, Recipe, Tag
from users.models import User

import django_filters as filters
from django_filters.rest_framework import AllValuesMultipleFilter

class RecipeFilter(filters.FilterSet):
    """Custom filterset for Recipe
    search by tags, name, author."""

    tags = filters.CharFilter(method="get_tags")
    author = filters.CharFilter(method="get_author")
    #favorite =  AllValuesMultipleFilter(methods="get_favorite")
    #cart = AllValuesMultipleFilter(field_name="cart__user_id")

    def get_tags(self, queryset, field_name, value):
        print (queryset)
        print (field_name)
        print ('value', value)
        
        #queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        print ('tags', tags)
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()
        return queryset
    
    def get_author(self, queryset, field_name, value):
        print (queryset)
        print (field_name)
        print ('value', value)
        
        author = self.request.query_params.get('author')
        print ('author', author)
        if author:
            queryset = queryset.filter(author=author)
        user = self.request.user
        if user.is_anonymous:
            return queryset
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'tags',
        )

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





# РАБОТАЕТ обычный поиск с учетом регистра
# class IngredientFilter(FilterSet):
#     name = filters.CharFilter(field_name='name', lookup_expr='icontains')

#     class Meta:
#         model = Ingredient
#         fields = ('name',)

# НЕ РАБОТАЕТ
# class IngredientFilter(FilterSet):
#     search = filters.CharFilter(field_name='name', method='filter_search')

#     def filter_search(self, queryset, name, value):
#         print ('=====================')
#         print ('queryset', queryset)
#         print ('name', name)
#         print ('value', value)
#         return queryset.annotate(
#             search=SearchVector('name')
#         ).filter(search=value)

#     class Meta:
#         model = Ingredient
#         fields = ('name',)

# НЕ РАБОТАЕТ
# class IngredientFilter(BaseFilterBackend):
#     queryset = Ingredient.objects.all()
#     name = filters.CharFilter(field_name='name')
#     print ('=====================')
#     #print (queryset)
#     def filter_queryset(self, request, queryset, view):
#         queryset = self.queryset
#         name = self.request.query_params.get('name')
#         if name:
#             queryset = queryset.annotate(
#                 search=SearchVector('name'),
#             ).filter(search__icontains=name)
#         return queryset
