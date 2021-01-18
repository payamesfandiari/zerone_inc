from django.apps import AppConfig


class ZeroslackConfig(AppConfig):
    name = 'zerone_inc.zeroslack'

    verbose_name = "ZerOne Slack"

    def ready(self):
        try:
            import zerone_inc.zeroslack.signals  # noqa F401
        except ImportError:
            pass

