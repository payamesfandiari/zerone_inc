import logging
from datetime import date
from django.contrib import messages
from django.db.models import QuerySet
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.views.generic import View, TemplateView
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse

from .exporter.csv.survey2csv import Survey2Csv
from .decorators import survey_available
from .forms import ResponseForm
from .models import SurveyForUser, Response, Answer, Category, Survey, Question

LOGGER = logging.getLogger(__name__)


# Create your views here.

class SurveyList(LoginRequiredMixin, ListView):
    model = SurveyForUser
    template_name = 'okr/survey_list.html'

    def get_queryset(self) -> QuerySet:
        qs = self.model.objects.filter(user=self.request.user, is_valid=True)
        return qs


class ConfirmView(TemplateView):
    template_name = "okr/confirm.html"

    def get_context_data(self, **kwargs):
        context = super(ConfirmView, self).get_context_data(**kwargs)
        context["uuid"] = kwargs["uuid"]
        context["response"] = Response.objects.get(interview_uuid=kwargs["uuid"])
        return context


class IndexView(TemplateView):
    template_name = "okr/list.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        surveys = Survey.objects.filter(
            is_published=True, expire_date__gte=date.today(), publish_date__lte=date.today()
        )
        if not self.request.user.is_authenticated:
            surveys = surveys.filter(need_logged_user=False)
        context["surveys"] = surveys
        return context


class SurveyCompleted(TemplateView):
    template_name = "okr/completed.html"

    def get_context_data(self, **kwargs):
        context = {}
        survey = get_object_or_404(Survey, is_published=True, id=kwargs["id"])
        context["survey"] = survey
        return context


class SurveyDetail(View):
    @survey_available
    def get(self, request, *args, **kwargs):
        survey = kwargs.get("survey")
        step = kwargs.get("step", 0)
        if survey.template is not None and len(survey.template) > 4:
            template_name = survey.template
        else:
            if survey.is_all_in_one_page():
                template_name = "okr/one_page_survey.html"
            else:
                template_name = "okr/survey.html"
        if survey.need_logged_user and not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))

        form = ResponseForm(survey=survey, user=request.user, step=step)
        categories = form.current_categories()

        asset_context = {
            # If any of the widgets of the current form has a "date" class, flatpickr will be loaded into the template
            "flatpickr": any([field.widget.attrs.get("class") == "date" for _, field in form.fields.items()])
        }
        context = {
            "response_form": form,
            "survey": survey,
            "categories": categories,
            "step": step,
            "asset_context": asset_context,
        }

        return render(request, template_name, context)

    @survey_available
    def post(self, request, *args, **kwargs):
        survey = kwargs.get("survey")
        if survey.need_logged_user and not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))

        form = ResponseForm(request.POST, survey=survey, user=request.user, step=kwargs.get("step", 0))
        categories = form.current_categories()

        if not survey.editable_answers and form.response is not None:
            LOGGER.info("Redirects to survey list after trying to edit non editable answer.")
            return redirect(reverse("okr:survey-list"))
        context = {"response_form": form, "survey": survey, "categories": categories}
        if form.is_valid():
            return self.treat_valid_form(form, kwargs, request, survey)
        return self.handle_invalid_form(context, form, request, survey)

    @staticmethod
    def handle_invalid_form(context, form, request, survey):
        LOGGER.info("Non valid form: <%s>", form)
        if survey.template is not None and len(survey.template) > 4:
            template_name = survey.template
        else:
            if survey.is_all_in_one_page():
                template_name = "okr/one_page_survey.html"
            else:
                template_name = "okr/survey.html"
        return render(request, template_name, context)

    def treat_valid_form(self, form, kwargs, request, survey):
        session_key = "survey_%s" % (kwargs["id"],)
        if session_key not in request.session:
            request.session[session_key] = {}
        for key, value in list(form.cleaned_data.items()):
            request.session[session_key][key] = value
            request.session.modified = True
        next_url = form.next_step_url()
        response = None
        if survey.is_all_in_one_page():
            response = form.save()
        else:
            # when it's the last step
            if not form.has_next_step():
                save_form = ResponseForm(request.session[session_key], survey=survey, user=request.user)
                if save_form.is_valid():
                    response = save_form.save()
                else:
                    LOGGER.warning("A step of the multipage form failed but should have been discovered before.")
        # if there is a next step
        if next_url is not None:
            return redirect(next_url)
        del request.session[session_key]
        if response is None:
            return redirect(reverse("okr:survey-list"))
        next_ = request.session.get("next", None)
        if next_ is not None:
            if "next" in request.session:
                del request.session["next"]
            return redirect(next_)
        return redirect("okr:survey-confirmation", uuid=response.interview_uuid)


def serve_unprotected_result_csv(survey):
    """ Return the csv corresponding to a survey. """
    survey_to_csv = Survey2Csv(survey)
    if survey_to_csv.need_update():
        survey_to_csv.generate_file()
    with open(survey_to_csv.filename, "r") as csv_file:
        response = HttpResponse(csv_file.read(), content_type="text/csv")
    content_disposition = 'attachment; filename="{}.csv"'.format(survey.name)
    response["Content-Disposition"] = content_disposition
    return response


@login_required
def serve_protected_result(request, survey):
    """ Return the csv only if the user is logged. """
    return serve_unprotected_result_csv(survey)


def serve_result_csv(request, primary_key):
    """ ... only if the survey does not require login or the user is logged.

    :param int primary_key: The primary key of the survey. """
    survey = get_object_or_404(Survey, pk=primary_key)
    if not survey.is_published:
        messages.error(request, "This survey has not been published")
        return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
    if survey.need_logged_user:
        return serve_protected_result(request, survey)
    return serve_unprotected_result_csv(survey)
