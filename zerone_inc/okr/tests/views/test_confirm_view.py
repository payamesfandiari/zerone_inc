# -*- coding: utf-8 -*-

from django.urls.base import reverse

from survey.models import Response, Survey
from survey.tests.base_test import BaseTest


class TestConfirmView(BaseTest):
    def get_first_response(self, survey_name):
        survey = Survey.objects.get(name=survey_name)
        responses = Response.objects.filter(survey=survey)
        response = responses.all()[0]
        url = reverse("survey-confirmation", args=(response.interview_uuid,))
        return self.client.get(url)

    def test_editable_survey(self):
        response = self.get_first_response("Unicode问卷")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "come back and change them")

    def test_uneditable_survey(self):
        response = self.get_first_response("Test survëy")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "come back and change them")
