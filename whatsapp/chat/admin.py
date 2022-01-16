from django.contrib import admin
from .models import User, Otp, Room, Messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

@admin.register(User)
class UserAdmin(DjangoUserAdmin):

    fieldsets = (
        (None, {'fields': ('contact', 'name', 'dp')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('contact', 'name', 'dp'),
        }),
    )
    list_display = ('contact', 'name', 'is_staff')
    search_fields = ('contact', 'name')
    ordering = ('contact',)


# Register your models here.
admin.site.register(Otp)
admin.site.register(Room)
admin.site.register(Messages)
