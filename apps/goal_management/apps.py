from django.apps import AppConfig

class GoalManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.goal_management'

    def ready(self):
        import apps.goal_management.search_indexes
        from . import signal