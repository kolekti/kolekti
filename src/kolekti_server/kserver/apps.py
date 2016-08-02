from django.apps import AppConfig


class KserverConfig(AppConfig):
    name = 'kserver'
    def ready(self):
        import kserver.signals
