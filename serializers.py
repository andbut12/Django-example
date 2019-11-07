import ast

from django.conf import settings
from rest_framework import serializers

from core.utils import resize_image
from .models import User, Group, Note, Diploma
from datetime import datetime, timedelta


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField(read_only=True)
    groups = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    short_name = serializers.SerializerMethodField(read_only=True)
    custom_fields = serializers.SerializerMethodField(read_only=True)

    def get_tags(self, obj):
        return [{'id': tag.id, 'title': tag.title} for tag in obj.tags.all()]

    def get_role(self, obj):
        return {'value': obj.role, 'title': obj.get_role_display()}

    def get_groups(self, obj):
        return [{'id': group.id, 'title': group.title} for group in obj.groups.all()]

    def get_avatar(self, obj):
        return obj.avatar.url if obj.avatar else '/static/images/default-profile.jpg'

    def get_full_name(self, obj):
        return obj.full_name

    def get_short_name(self, obj):
        return obj.short_name

    def get_custom_fields(self, obj):
        """
        For organization.models.CustomField,
        :return: list of [name, value, visible, type]
        for custom fields
        """
        qs = obj.site.organization.custom_fields
        names = qs.values_list('name', flat=True)
        fields = list()
        for name in names:
            field = qs.get(name=name)
            values = field.values.get(obj.email)
            if values and field.field_type == 5:  # 5 is MultipleChoice
                values = ', '.join(ast.literal_eval(values))  # Represent "[1, 2]" like "1, 2"
            fields.append([name, values, field.visible, field.field_type])
        return fields

    class Meta:
        model = User
        exclude = ['site', 'is_staff', 'is_paid', 'is_active', 'password',
                   'unsubscribe_code', 'is_unsubscribed', 'user_permissions']


class UserWriteSerializer(serializers.ModelSerializer):
    def validate_avatar(self, value):
        if value:
            return resize_image(value, 'user_avatar')
        else:
            return

    class Meta:
        model = User
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    users = UserSerializer(read_only=True, many=True)
    is_active = serializers.SerializerMethodField(read_only=True)
    can_edit = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    payment = serializers.SerializerMethodField(read_only=True)

    def get_payment(self, obj):
        return obj.access_requests.filter(payment__is_paid=True).count()

    def get_status(self, obj):
        status = 'Обучение'
        if obj.date_start and obj.date_end and obj.duration:
            if obj.date_start <= datetime.now().date() <= obj.date_end:
                status = 'Набор'
            else:
                if obj.date_end + timedelta(obj.duration) < datetime.now().date():
                    status = 'Завершено'
        return status

    def get_is_active(self, obj):
        return obj.access_requests.filter(access=True).exists()

    def get_can_edit(self, obj):
        user = self.context['request'].user
        if user.is_anonymous():
            return False

        if user.role == 'student':
            return False

        if user.role == 'teacher':
            for request in obj.access_requests.all():
                if user in request.course.authors.all():
                    return True

            if user == obj.author:
                return True

        if user.role == 'admin':
            return True

        return False

    class Meta:
        model = Group
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = '__all__'


class DiplomaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True)

    def get_description(self, obj):
        return obj.description

    def get_image(self, obj):
        return obj.image.url if obj.image else '/static/images/default_certificate.png'

    class Meta:
        model = Diploma
        fields = '__all__'

class DiplomaWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Diploma
        fields = '__all__'


class NoteWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = '__all__'
