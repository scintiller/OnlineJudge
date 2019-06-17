from django.conf.urls import url

from ..views.admin import CourseAPI, PowerPointAPI

urlpatterns = [
    url(r"^course/?$", CourseAPI.as_view(), name="course_admin_api"),
    url(r"^course/ppt/?$", PowerPointAPI.as_view(), name="ppt_admin_api"),
]