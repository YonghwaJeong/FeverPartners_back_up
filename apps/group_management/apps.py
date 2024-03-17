from django.apps import AppConfig


class GroupManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.group_management'

    def ready(self):
        import apps.group_management.search_indexes
        from . import signal