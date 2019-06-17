from django.conf.urls import url
from ..views.admin import SolutionVideoAPI

urlpatterns = [
    url(r'^upload/solution_video/?$', SolutionVideoAPI.as_view(), name='solution_video_admin_api'),
]