from django.apps import AppConfig

class KserverSaasConfig(AppConfig):
    name = 'kserver_saas'

    def ready(self):
        import kserver_saas.signals
