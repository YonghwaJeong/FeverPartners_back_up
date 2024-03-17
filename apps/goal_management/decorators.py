from django.http import HttpResponseForbidden
from functools import wraps
from apps.goal_management.models import Goal

def goal_ownership_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        goal_id = kwargs.get('goal_id')
        try:
            goal = Goal.objects.get(pk=goal_id)
            if request.user != goal.user:
                return HttpResponseForbidden("페이지에 접근할 권한이 없습니다.")
        except Exception:
            return HttpResponseForbidden("잘못된 접근방식입니다.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view