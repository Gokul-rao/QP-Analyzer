from django.apps import AppConfig

from .shared.models_loader import load_models


class AnalyzeappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyzeApp'

    def ready(self):
        load_models()