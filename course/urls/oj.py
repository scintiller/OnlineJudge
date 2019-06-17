from django.conf.urls import url

from ..views.oj import CourseAPI, PowerPointAPI

urlpatterns = [
    url(r"^course/?$", CourseAPI.as_view(), name="course_api"),
    url(r"^course/ppt/?$", PowerPointAPI.as_view(), name="ppt_api")
]
