from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'role', 'username', 
                    'first_name', 'last_name', 'email',)
    search_fields = ('username','email')
    list_filter = ('email', 'role', 'username',)
    empty_value_display = '-пусто-'
    save_on_top = True
