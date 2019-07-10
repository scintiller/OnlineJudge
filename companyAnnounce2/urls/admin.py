from django.conf.urls import url

from ..views.admin import AnnouncementAdminAPI

urlpatterns = [
    url(r"^company/notification/?$", AnnouncementAdminAPI.as_view(), name="company_notification_admin_api"),
]
