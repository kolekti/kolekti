from django.apps import AppConfig
import sys
import locale

class KserverConfig(AppConfig):
    name = 'kserver'


    def ready(self):
        import kserver.signals
