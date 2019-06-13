from django.conf.urls import url

from ..views.admin import CourseAPI

urlpatterns = [
    url(r"^course/?$", CourseAPI.as_view(), name="course_admin_api"),
]