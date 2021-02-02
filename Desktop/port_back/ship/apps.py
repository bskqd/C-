from django.apps import AppConfig


class ShipConfig(AppConfig):
    name = 'ship'

    def ready(self):
        import ship.signals
