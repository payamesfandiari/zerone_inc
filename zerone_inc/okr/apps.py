from django.apps import AppConfig


class OkrConfig(AppConfig):
    name = 'zerone_inc.okr'
    verbose_name = "OKR"

    def ready(self) -> None:
        try:
            import zerone_inc.okr.signals  # noqa F401
        except ImportError:
            pass

