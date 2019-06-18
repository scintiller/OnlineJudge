from account.decorators import super_admin_required
from judge.tasks import judge_task
# from judge.dispatcher import JudgeDispatcher
from utils.api import APIView
from ..models import Submission
from ..serializers import SubmissionListSerializer


## root 有权利让某道题重新被评判
class SubmissionRejudgeAPI(APIView):
    @super_admin_required
    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return self.error("Parameter error, id is required")
        try:
            submission = Submission.objects.select_related("problem").get(id=id, contest_id__isnull=True)
        except Submission.DoesNotExist:
            return self.error("Submission does not exists")
        submission.statistic_info = {}
        submission.save()

        judge_task.send(submission.id, submission.problem.id)
        return self.success()


class ClassSubmissionListAPI(APIView):
    def get(self, request):
        if not request.GET.get("problem_id"):
            return self.error("problem id is needed")
        if not request.GET.get("user_name"):
            return self.error("user name is needed")

        submissions = Submission.objects.filter(contest_id__isnull=True).order_by('-create_time')
        problem_id = request.GET.get("problem_id")
        username = request.GET.get("username")
        # 筛选：只看某道题
        if problem_id:
            try:
                problem = Problem.objects.get(_id=problem_id, contest_id__isnull=True, visible=True)
            except Problem.DoesNotExist:
                return self.error("Problem doesn't exist")
            submissions = submissions.filter(problem=problem)
        # 筛选：只看某个用户（只看自己，或按用户名搜索）
        if username:
            submissions = submissions.filter(username=username)

        return self.success(SubmissionListSerializer(submissions[0]).data)
