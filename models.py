import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from email_validator import validate_email


class UserManager(BaseUserManager):
    def _create_user(self, email, password, site,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not site:
            raise ValueError('The given site must be set')

        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff,
                          is_superuser=is_superuser,
                          site=site,
                          last_login=now,
                          registered_at=now,
                          **extra_fields)
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create(self, **extra_fields):
        email = extra_fields.pop('email')
        site = extra_fields.pop('site', Site.objects.first())
        password = extra_fields.pop('password')
        return self.create_user(email, password, site, **extra_fields)

    def create_user(self, email=None, password=None, site=None, **extra_fields):
        return self._create_user(email, password, site, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, Site.objects.first(), True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_TYPES = [
        ['student', 'Ученик'],
        ['teacher', 'Преподаватель'],
        ['admin', 'Администратор']
    ]
    GRADE_TYPES = [
        ['Нет', 'Нет'],
        ['Кандидат психологических наук', 'Кандидат психологических наук'],
        ['Доктор медицинских наук', 'Доктор медицинских наук']
    ]
    SPECIALITY_TYPES = [
        ['Психолог', 'Психолог'],
        ['Клинический психолог', 'Клинический психолог'],
        ['Врач-психотерапевт', 'Врач-психотерапевт'],
        ['Врач-психиатр', 'Врач-психиатр']
    ]
    GENDER_TYPES = [
        ['Мужской', 'Мужской'],
        ['Женский', 'Женский']
    ]
    EXAMINATION_TYPES = [
        ['Не производилось', 'Не производилось'],
        ['Производилось', 'Производилось']
    ]

    site = models.ForeignKey(Site, verbose_name='Сайт', related_name='users')
    first_name = models.CharField(verbose_name='Имя', max_length=30, blank=False)
    last_name = models.CharField(verbose_name='Фамилия', max_length=30, blank=False)
    middle_name = models.CharField(verbose_name='Отчество', max_length=30, blank=True)
    avatar = models.ImageField(verbose_name='Аватар', blank=True)
    email = models.EmailField(verbose_name='Электронная почта', max_length=255)
    role = models.CharField(verbose_name='Роль', max_length=20, choices=ROLE_TYPES, default=ROLE_TYPES[0][0])
    groups = models.ManyToManyField('user.Group', verbose_name='Группы', related_name='users', blank=True)

    # Box fields
    tags = models.ManyToManyField('organization.Tag', verbose_name='Тэги', related_name='users', blank=True)
    city = models.CharField(verbose_name='Город', max_length=100, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=200, blank=True)
    grade = models.CharField(verbose_name='Ученая степень', max_length=50, choices=GRADE_TYPES, default=GRADE_TYPES[0][0])
    gender = models.CharField(verbose_name='Пол', max_length=50, choices=GENDER_TYPES, default=GENDER_TYPES[0][0])
    speciality = models.CharField(verbose_name='Специальность', max_length=50, choices=SPECIALITY_TYPES, default=SPECIALITY_TYPES[0][0])
    examination = models.CharField(verbose_name='Обследование', max_length=50, choices=EXAMINATION_TYPES, default=EXAMINATION_TYPES[0][0])

    phone = models.CharField(verbose_name='Телефон', max_length=30, blank=True)
    address = models.CharField(verbose_name='Адрес', max_length=200, blank=True)
    about = models.TextField(verbose_name='Обо мне', blank=True)

    is_active = models.BooleanField(verbose_name='Активен', default=True)
    is_staff = models.BooleanField(verbose_name='Сотрудник', default=False)
    is_paid = models.BooleanField(verbose_name='Оплачен', default=True)
    is_approved = models.BooleanField(verbose_name='Подтверждён', default=False)
    registered_at = models.DateTimeField(verbose_name='Зарегистрирован', default=timezone.now)

    unsubscribe_code = models.UUIDField(default=uuid.uuid4, editable=False)
    is_unsubscribed = models.BooleanField(verbose_name='Отписка', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()
    on_site = CurrentSiteManager()

    class Meta:
        unique_together = ['site', 'email']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def full_name(self):
        return '{} {} {}'.format(self.last_name, self.first_name, self.middle_name)
    full_name.fget.short_description = 'Полное имя'

    @property
    def short_name(self):
        return '{} {}{}'.format(self.last_name,
                                self.first_name[0] + '.' if self.first_name else '',
                                self.middle_name[0] + '.' if self.middle_name else '')

    def get_short_name(self):
        return self.short_name

    def get_full_name(self):
        return self.full_name

    @property
    def organization(self):
        return self.site.organization
    organization.fget.short_description = 'Организация'

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        try:
            validate_email(self.email, check_deliverability=True)
            send_mail(subject, message, from_email, [self.email], **kwargs)
        except:
            pass

    def __str__(self):
        return '({}) - {} - {}'.format(self.site.domain, self.email, self.full_name)


class Group(models.Model):
    site = models.ForeignKey(Site, verbose_name='Сайт')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Создатель', blank=True, null=True, on_delete=models.SET_NULL)
    title = models.CharField(verbose_name='Название группы', max_length=60)
    course = models.ForeignKey('course.Course', verbose_name='Курс', related_name='group', blank=True, null=True)
    limit_access = models.PositiveSmallIntegerField(verbose_name='Ограничение заявок', default=10)

    date_start = models.DateField(verbose_name='Дата начала набора', blank=True, null=True)
    date_end = models.DateField(verbose_name='Дата окончания набора', blank=True, null=True)

    duration = models.PositiveSmallIntegerField(verbose_name='Продолжительность доступа', default=30)

    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Diploma(models.Model):
    site = models.ForeignKey(Site, verbose_name='Сайт')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Владелец', blank=True, null=True, on_delete=models.SET_NULL)
    description = models.CharField(verbose_name='Доп. информация', max_length=155, blank=True)
    image = models.ImageField(verbose_name='Изображение', blank=True)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Диплом'
        verbose_name_plural = 'Дипломы'


class Note(models.Model):
    TYPES = [
        ['Клинический диагноз', 'Клинический диагноз'],
        ['Жалобы', 'Жалобы'],
        ['Текущее состояние', 'Текущее состояние'],
        ['Заметки', 'Заметки']
    ]
    site = models.ForeignKey(Site, verbose_name='Сайт')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Автор', related_name='anotes', blank=True, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', blank=True, null=True, on_delete=models.SET_NULL)

    type = models.CharField(verbose_name='Тип записи', max_length=50, choices=TYPES, default=TYPES[0][0])
    title = models.CharField(verbose_name='Заголовок', max_length=60, blank=True, null=True)
    text = models.TextField(verbose_name='Текст записи', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Запись о пользователе'
        verbose_name_plural = 'Записи о пользователях'
