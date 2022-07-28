from django.db import models
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """
    Поиск сначала по точному совпадению,
    потом по вхождению в слове
    """
    name = filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):
        q1 = queryset.filter(name__iexact=value).annotate(
            q_ord=models.Value(0, models.IntegerField()))
        q2 = queryset.filter(name__icontains=value).annotate(
            q_ord=models.Value(1, models.IntegerField()))
        return q1.union(q2).order_by('q_ord')


class RecipeFilters(FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        method='filter_tags'
    )
    author = filters.AllValuesFilter(
        method='filter_author'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, queryset, name, value):
        if value:
            return queryset.filter(
                tags__slug__in=value).distinct()
        return queryset

    def filter_author(self, queryset, name, value):
        if value:
            return queryset.filter(author=value)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite=self.request.user.id)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(cart=self.request.user.id)
        return queryset
