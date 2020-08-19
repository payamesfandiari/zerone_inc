from django.contrib import admin

from .actions import make_published
from .exporter.csv import Survey2Csv
from .models import Answer, Category, Question, Response, Survey, SurveyForUser


@admin.register(SurveyForUser)
class OkrAdmin(admin.ModelAdmin):
    list_display = ["user", "survey", "is_valid", "assigned_date"]
    search_fields = ["user"]
    list_filter = ["is_valid", "user"]


class QuestionForSurveyInline(admin.TabularInline):
    model = Question.survey.through


class QuestionAdmin(admin.ModelAdmin):
    model = Question
    list_display = (
        "text",
        "required",
        "category",
        "type",
        "choices",
    )
    exclude = ('survey',)


class CategoryInline(admin.StackedInline):
    model = Category
    extra = 0


class SurveyAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "need_logged_user", "template")
    list_filter = ("is_published", "need_logged_user")
    inlines = [CategoryInline, QuestionForSurveyInline]
    actions = [make_published, Survey2Csv.export_as_csv]


class AnswerBaseInline(admin.StackedInline):
    fields = ("question", "body")
    readonly_fields = ("question",)
    extra = 0
    model = Answer


class ResponseAdmin(admin.ModelAdmin):
    list_display = ("interview_uuid", "survey", "created", "user")
    list_filter = ("survey", "created")
    date_hierarchy = "created"
    inlines = [AnswerBaseInline]
    # specifies the order as well as which fields to act on
    readonly_fields = ("survey", "created", "updated", "interview_uuid", "user")


admin.site.register(Question, QuestionAdmin)
# admin.site.register(Category, CategoryInline)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Response, ResponseAdmin)
