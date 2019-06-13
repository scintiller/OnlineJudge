from django.conf.urls import url

from ..views.oj import CourseAPI

urlpatterns = [
    url(r"^course/?$", CourseAPI.as_view(), name="course_api"),
]
