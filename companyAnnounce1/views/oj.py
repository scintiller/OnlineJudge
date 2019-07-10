from utils.api import APIView

from companyAnnounce1.models import Announcement1
from companyAnnounce1.serializers import AnnouncementSerializer


class AnnouncementAPI(APIView):
    def get(self, request):
        announcements = Announcement1.objects.filter(visible=True)
        return self.success(self.paginate_data(request, announcements, AnnouncementSerializer))
