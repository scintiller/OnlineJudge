from django.conf.urls import url

from ..views.admin import UserAdminAPI, GenerateUserAPI, ClassAdminAPI, ClassStudentAPI, SetClassAPI
urlpatterns = [
    url(r"^user/?$", UserAdminAPI.as_view(), name="user_admin_api"),
    url(r"^generate_user/?$", GenerateUserAPI.as_view(), name="generate_user_api"),
    url(r"^class/?$", ClassAdminAPI.as_view(), name="class_admin_api"),
    url(r"^set_class/?$", SetClassAPI.as_view(), name="set_class_api"),
    url(r"^class_student/?$", ClassStudentAPI.as_view(), name="class_student_api")
]
