from django.conf.urls import url

from ..views.oj import AnnouncementAPI

urlpatterns = [
    url(r"^company/announcement/?$", AnnouncementAPI.as_view(), name="company_announcement_api"),
]
