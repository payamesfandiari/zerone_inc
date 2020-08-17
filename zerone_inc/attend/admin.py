from django.contrib import admin

# Register your models here.


from .models import Attendance


@admin.register(Attendance)
class OkrAdmin(admin.ModelAdmin):
    list_display = ["user"]
    search_fields = ["user"]
    list_filter = ["user"]
