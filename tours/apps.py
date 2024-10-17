from django.apps import AppConfig


class ToursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tours'
    
    def ready(self):
        import tours.signals  # Import the signals file to ensure they get connected
