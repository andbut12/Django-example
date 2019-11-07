from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'user'
    verbose_name = 'Пользователи'

    def ready(self):
        import user.signals