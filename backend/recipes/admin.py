from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Ingredient, IngredientAmount, Recipe, Tag


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'amount', 'recipe')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    save_on_top = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'get_image',)
    readonly_fields: ('get_image',)
    fields = (
        ('name', 'cooking_time',),
        ('author', 'tags',),
        ('text',),
        ('image',),
    )
    raw_id_fields = ('author', )
    search_fields = (
        'name', 'author__username', 'author__email'
    )
    list_filter = (
        'name', 'author__username',
    )
    save_on_top = True
    inlines = (IngredientInline,)

    def get_image(self, obj):
        """
        пиктограмма изображения в админ панели
        """
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30">')
    get_image.short_description = 'Изображение'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_code', 'slug',)
    search_fields = ('name', 'color',)
