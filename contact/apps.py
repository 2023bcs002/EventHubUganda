from django.apps import AppConfig


class ContactConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contact'
    verbose_name = 'Contact Management'

    def ready(self):
        pass  # Add any app initialization here if needed
