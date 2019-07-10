from django.conf.urls import url

from ..views.admin import AnnouncementAdminAPI

urlpatterns = [
    url(r"^company/announcement/?$", AnnouncementAdminAPI.as_view(), name="company_announcement_admin_api"),
]
