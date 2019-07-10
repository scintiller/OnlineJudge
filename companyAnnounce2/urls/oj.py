from django.conf.urls import url

from ..views.oj import AnnouncementAPI

urlpatterns = [
    url(r"^company/notification/?$", AnnouncementAPI.as_view(), name="company_notification_api"),
]
