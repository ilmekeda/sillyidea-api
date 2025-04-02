''''
Django admin customization
'''
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as translate

from core import models


class UserAdmin(BaseUserAdmin):
    '''Define the admin pages for the users'''

    ordering = ['id']
    list_display = ['email', 'last_name', 'first_name']
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'password',
                )
            }
        ),
        (
            translate('Permissions'),
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (
            translate('Important dates'),
            {
                'fields': (
                    'last_login',
                )
            }
        ),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),  # custom css
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'first_name',
                    'last_name',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
    )


admin.site.register(models.User, UserAdmin)
