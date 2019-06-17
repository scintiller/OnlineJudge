from django.conf.urls import url
from ..views.admin import ProblemSolutionAPI

urlpatterns = [
    url(r'^problem/solution/?$', ProblemSolutionAPI.as_view(), name='problem_solution_admin_api'),
]