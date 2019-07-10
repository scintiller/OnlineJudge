from utils.api import APIView

from companyAnnounce2.models import Announcement2
from companyAnnounce2.serializers import AnnouncementSerializer


class AnnouncementAPI(APIView):
    def get(self, request):
        announcements = Announcement2.objects.filter(visible=True)
        return self.success(self.paginate_data(request, announcements, AnnouncementSerializer))
