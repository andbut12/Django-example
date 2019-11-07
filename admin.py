from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group as djangoGroup
from django.contrib.sites.models import Site

from user.forms import UserFormCreate, UserFormChange
from .models import User, Group, Note, Diploma


@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = UserFormCreate
    form = UserFormChange
    fieldsets = [
        ['Персональная информация', {
            'fields': ['site', 'password', 'city', 'position', 'grade', 'speciality', 'role', 'last_name', 'first_name',
                       'middle_name', 'groups', 'avatar', 'about', 'tags']}],
        ['Контакты', {'fields': ['email', 'phone', 'address']}],
        ['Настройки', {'fields': ['is_active', 'is_paid', 'is_staff', 'is_superuser', 'is_approved']}],
        ['Важные даты', {'fields': ['last_login', 'registered_at']}],
    ]
    add_fieldsets = [
        [None, {
            'classes': ['wide'],
            'fields': ['site', 'email', 'password'],
        }],
    ]
    readonly_fields = ['last_login', 'registered_at']
    list_display = ['full_name', 'organization', 'email', 'phone', 'site', 'registered_at']
    list_filter = ['role', 'is_active', 'site__organization']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'site__domain', 'site__organization__title']
    ordering = ['-registered_at']

    def get_form(self, request, obj=None, **kwargs):
        # By passing 'fields', we prevent ModelAdmin.get_form from
        # looking up the fields itself by calling self.get_fieldsets()
        # If you do not do this you will get an error from
        # modelform_factory complaining about non-existent fields.
        if obj:
            kwargs['fields'] = flatten_fieldsets(self.fieldsets)
        return super(UserAdmin, self).get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(UserAdmin, self).get_fieldsets(request, obj)
        newfieldsets = list(fieldsets)
        if obj:
            fields = list(obj.site.organization.custom_fields.values_list('name', flat=True))
            newfieldsets.append(['Дополнительные параметры', {'fields': fields}])
        return newfieldsets


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ['users']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    pass


@admin.register(Diploma)
class DiplomaAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(Site)
admin.site.unregister(djangoGroup)
