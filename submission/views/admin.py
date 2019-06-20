from account.decorators import super_admin_required
from judge.tasks import judge_task
# from judge.dispatcher import JudgeDispatcher
from utils.api import APIView
from ..models import Submission, Problem
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
        if not request.GET.get("class_name"):
            return self.error("class name is needed")

        class_name = request.GET.get("class_name")
        problem_id = request.GET.get("problem_id")
        try:
            c = Class.objects.get(class_name=class_name)
        except Class.DoesNotExist:
            return self.error("Class does not exist")
        try:
            problem = Problem.objects.get(_id=problem_id, contest_id__isnull=True, visible=True)
        except Problem.DoesNotExist:
            return self.error("Problem doesn't exist")

        students = c.user_set.all()
        data = {}
        for s in students:
            submissions = Submission.objects.filter(contest_id__isnull=True).order_by('-create_time')
            submissions = submissions.filter(problem=problem)
            submissions = submissions.filter(username=s.username)

            if len(submissions) != 0:
                data[s.user_name] = SubmissionModelSerializer(submissions[0]).data
            else:
                data[s.user_name] = {}

        return self.success(data)
