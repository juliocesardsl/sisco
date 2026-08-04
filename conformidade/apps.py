from django.apps import AppConfig


class ConformidadeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'conformidade'
    verbose_name = 'Conformidade'

    def ready(self):
        from . import signals  # noqa: F401
