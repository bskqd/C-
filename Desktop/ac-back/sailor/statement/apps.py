from django.apps import AppConfig


class StatementConfig(AppConfig):
    name = 'sailor.statement'

    def ready(self):
        import sailor.statement.signals
