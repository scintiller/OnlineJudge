from django.conf.urls import url
from ..views.oj import SolutionVideoAPI

urlpatterns = [
    url(r'^problem/solution/?$', SolutionVideoAPI.as_view(), name='problem_solution_api'),
]