from django.conf.urls import url
from ..views.oj import SolutionVideoAPI

urlpatterns = [
    url(r'^solution_video/?$', SolutionVideoAPI.as_view(), name='solution_video_api'),
]