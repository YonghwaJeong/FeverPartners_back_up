from django.http import HttpResponseForbidden
from functools import wraps
from apps.group_management.models import Room

def room_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        room_id = kwargs.get('room_id')
        try:
            room = Room.objects.get(pk=room_id)
            if request.user != room.master:
                return HttpResponseForbidden("관리페이지에 접근할 권한이 없습니다.")
        except Exception:
            return HttpResponseForbidden("잘못된 접근방식입니다.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view