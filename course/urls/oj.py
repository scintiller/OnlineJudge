from django.conf.urls import url

from ..views.oj import CourseAPI, PowerPointAPI, FileDownloadAPI, ImageUploadAPIView, FileUploadAPIView

urlpatterns = [
    url(r"^course/?$", CourseAPI.as_view(), name="course_api"),
    url(r"^course/ppt/?$", PowerPointAPI.as_view(), name="ppt_api"),
    url(r"^download/?$", FileDownloadAPI.as_view(), name = "download_file"),
    url(r"^upload_image/?$", ImageUploadAPIView.as_view(), name="upload_image"),
    url(r"^upload_file/?$", FileUploadAPIView.as_view(), name="upload_file"),
]
