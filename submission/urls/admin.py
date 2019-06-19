from django.conf.urls import url

from ..views.admin import SubmissionRejudgeAPI, ClassSubmissionListAPI

urlpatterns = [
    url(r"^submission/rejudge?$", SubmissionRejudgeAPI.as_view(), name="submission_rejudge_api"),
    url(r"^class_submission/?$", ClassSubmissionListAPI.as_view(), name="class_submission_api"),
]
