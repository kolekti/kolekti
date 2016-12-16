from django.apps import AppConfig
import sys
import locale



class KserverSaasConfig(AppConfig):
    name = 'kserver_saas'


    def ready(self):
        import kserver_saas.signals
