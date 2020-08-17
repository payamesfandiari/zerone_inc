from django.contrib import admin


from .models import SurveyForUser


@admin.register(SurveyForUser)
class OkrAdmin(admin.ModelAdmin):
    list_display = ["user", "survey", "is_valid", "assigned_date"]
    search_fields = ["user"]
    list_filter = ["is_valid", "user"]
