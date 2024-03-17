from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from elastic_transport import Serializer
from apps.alarm.models import Alarm
from apps.goal_management.models import Goal
from apps.group_management.models import Room, User
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
import json
from .decorators import room_admin_required
from django.urls import reverse
from django.db.models import Sum
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from apps.group_activity.models import UserActivityInfo

# 이 부분 나중에 수정되어야 함
@room_admin_required
def show_admin_page(request, room_id):
    room = Room.objects.get(pk = room_id)
    ctx = {
        'room_id':room_id,
        'room' : room,
    }
    return render(request, 'group_administration/group_admin_base.html', ctx)

@room_admin_required
def show_member_list(request, room_id):
    room = Room.objects.get(pk = room_id)
    master = Room.objects.get(pk=room_id).master
    members = Room.objects.get(pk=room_id).members.exclude(pk=master.pk)
    cnt = {
        'members':members,
        'room_id':room_id,
        'room' : room,
    }
    return render(request, 'group_administration/group_member_list.html', cnt)

@require_http_methods(["DELETE"])
def expel_member(request):
    try:
        data = json.loads(request.body)
        room_id = data.get('roomId')
        member_id = data.get('memberId')

        room = Room.objects.get(pk=room_id)
        member = room.members.get(pk=member_id)

        # 추방에 따른 로직 => 관련 정보 수정 및 초기화
        target_goal = member.goal.filter(belonging_group_id=room_id).first()
        target_goal.is_in_group = False
        target_goal.belonging_group_id = None
        target_goal.save()

        room.members.remove(member)
        user_info = room.activity_infos.all().get(user=member)
        # 강퇴시 전액 환급
        member.coin += room.deposit
        member.save()
        room.penalty_bank -= (room.deposit - user_info.deposit_left)
        room.save()
        user_info.delete()
        return JsonResponse({'message': '멤버가 성공적으로 삭제되었습니다.'}, status=200)
    except Exception as e:
        print(e)
        return HttpResponse(status=400)

@require_http_methods(["POST"]) 
def transfer_master(request):
    try:
        data = json.loads(request.body)
        room_id = data.get('roomId')
        member_id = data.get('memberId')

        room = Room.objects.get(pk=room_id)
        room.master = room.members.get(pk=member_id)
        room.save()

        return JsonResponse({'message': '권한이 성공적으로 양도되었습니다.'}, status=200)
    except Exception:
        return HttpResponse(status=400)

@room_admin_required
def activate_room(request, room_id):
    try:
        room = Room.objects.get(pk=room_id)
        room.is_active = True
        room.closing_date = timezone.now() + room.duration
        room.save()
        url = reverse('group_activity:main_page', kwargs={'room_id': room_id})
        return redirect(url)
    except Exception as e:
        return HttpResponse(status=404)

@require_http_methods(["DELETE"])
def delete_room(request):
    try:
        data = json.loads(request.body)
        room_id = data.get('roomId')
        room = Room.objects.get(pk=room_id)

        # 징수한 벌금을 인증 성과에 따라 분배
        distribute_reward(room)
        # 폐쇄에 따른 로직 => 모든 멤버의 Goal 정보 수정 및 초기화(Master본인 포함)
        members = room.members.all()
        for member in members:
            target_goal = member.goal.filter(belonging_group_id=room_id).first()
            target_goal.is_in_group = False
            target_goal.belonging_group_id = None
            target_goal.save()

        room.delete()

        return JsonResponse({'message': '폐쇄 작업이 성공적으로 완료되었습니다.'}, status=200)
    except Exception:
        return HttpResponse(status=400)

def distribute_reward(room: Room):
    # 인증이 필수가 아닌 방은 벌금도 없으므로 바로 return
    if not room.cert_required:
        return
    activity_infos_in_room = room.activity_infos.all()
    total_count = activity_infos_in_room.aggregate(total_count=Sum('authentication_count'))['total_count']
    # 한 건의 인증도 이루어지지 않음 / 의미가 없으므로 바로 retrun
    if total_count == 0:
        return
    for activity_info in activity_infos_in_room:
        user = activity_info.user
        activity_count = activity_info.authentication_count
        penalty_bank = room.penalty_bank
        reward = (penalty_bank * activity_count) / total_count
        user.coin += int(reward)
        user.coin += activity_info.deposit_left
        print(user.nickname,"에게",reward,"코인의 보상을 지급.")
        user.save()

@room_admin_required  
def direct_invitation(request, room_id):
    room = Room.objects.get(pk=room_id)
    cnt = {
        'room_id':room_id,
        'room': room,
    }
    return render(request, 'group_administration/direct_invitation.html', cnt)

@room_admin_required
def search_users(request, room_id):
    nickname = request.GET.get('nickname')
    User = get_user_model()
    room_members = Room.objects.get(pk=room_id).members.all()
    users = User.objects.filter(nickname__icontains=nickname).exclude(pk__in=room_members.values_list('pk', flat=True))
    search_results = [{'nickname': user.nickname, 'id': user.pk, 'room_id': room_id} for user in users]

    return JsonResponse(search_results, safe=False)

@require_http_methods(["POST"])
def suggest_join(request, room_id):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        room = get_object_or_404(Room, id=room_id)
        user = get_object_or_404(get_user_model(), id=user_id)
        existing_alarm = Alarm.objects.filter(alarm_from=request.user, alarm_to=user, room=room).exists()
        if existing_alarm:
            return HttpResponse(status=403)
        Alarm.objects.create(alarm_from=request.user, alarm_to=user, goal = None, room = room)
        return HttpResponse(status=204)
    except Exception:
        return HttpResponse(status=400)