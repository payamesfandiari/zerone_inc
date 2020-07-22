from django.apps import AppConfig


class AttendConfig(AppConfig):
    name = 'zerone_inc.attend'

    verbose_name = "Attendance"

    def ready(self):
        try:
            import zerone_inc.attend.signals  # noqa F401
        except ImportError:
            pass
