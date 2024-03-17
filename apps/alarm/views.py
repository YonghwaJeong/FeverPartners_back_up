from django.shortcuts import redirect,render, get_object_or_404
from apps.alarm.models import Alarm
from apps.goal_management.models import Goal
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json
from apps.group_activity.models import UserActivityInfo

def delete(request, pk):
    if request.method == 'POST':
        Alarm.objects.get(id=pk).delete()
    return redirect('user_management:detail')

def show_alarms(request):
    alarms = Alarm.objects.filter(alarm_to=request.user) #현재 유저일때만
    cnt = {
        'alarms':alarms,
    }
    return render(request, 'alarm/alarms.html', cnt)

def alarm_detail_as_user(request, pk):
    alarm = get_object_or_404(Alarm, pk=pk)
    context = {
        'alarm': alarm,
    }
    return render(request, 'alarm/alarm_detail_from_group.html', context)

def alarm_detail_as_master(request, pk):
    alarm = get_object_or_404(Alarm, pk=pk)
    context = {
        'alarm': alarm,
    }
    return render(request, 'alarm/alarm_detail_from_user.html', context)

def alarm_detail_direct(request, pk):
    alarm = get_object_or_404(Alarm, pk=pk)
    goals = Goal.objects.filter(user=alarm.alarm_to)
    context = {
        'alarm': alarm,
        'goals':goals,
    }
    return render(request, 'alarm/alarm_detail_direct.html', context)

@login_required
def accept_request(request, alarm_id):
    alarm = get_object_or_404(Alarm, id=alarm_id)
    room = alarm.room
    goal = alarm.goal

    if goal.is_in_group or goal.is_completed:
        return HttpResponse(status=400)
    elif goal.user in room.members.all():
        return HttpResponse(status=409)

    if request.user == room.master:
        # 유저의 그룹에 대한 가입 요청 -> 요청을 보낸 유저를 방에 추가
        if alarm.alarm_from.coin < room.deposit:
            # 잔여 Coin이 부족한 경우
            return HttpResponse(status=403)
        room.members.add(alarm.alarm_from)
        goal.is_in_group = True
        goal.belonging_group_id = room.pk
        goal.save()
        UserActivityInfo.objects.create(
            user = alarm.alarm_from,
            room = room,
            deposit_left = room.deposit,
        )
        alarm.alarm_from.coin -= room.deposit
        alarm.alarm_from.save()
    else:
        # 다른 그룹의 관리자가 유저에게 가입 제안 -> 대상이 되는 유저를 방에 추가
        if alarm.alarm_to.coin < room.deposit:
            # 잔여 Coin이 부족한 경우
            return HttpResponse(status=403)
        room.members.add(alarm.alarm_to)
        goal.is_in_group = True
        goal.belonging_group_id = room.pk
        goal.save()
        UserActivityInfo.objects.create(
            user = alarm.alarm_to,
            room = room,
            deposit_left = room.deposit,
        )
        alarm.alarm_to.coin -= room.deposit
        alarm.alarm_to.save()
    alarm.delete()
    return HttpResponse(status=204)

def accept_direct_request(request, alarm_id):
    alarm = get_object_or_404(Alarm, id=alarm_id)
    room = alarm.room
    data = json.loads(request.body)
    goal_id = data.get('goal_id')
    goal = get_object_or_404(Goal, id=goal_id)
    if alarm.alarm_to in room.members.all():
        # 이미 방의 멤버인 상태
        return HttpResponse(status=400)
    elif alarm.alarm_to.coin < room.deposit:
        return HttpResponse(status=403)
    room.members.add(alarm.alarm_to)
    goal.is_in_group = True
    goal.belonging_group_id = room.pk
    goal.save()

    UserActivityInfo.objects.create(
        user = alarm.alarm_to,
        room = room,
        deposit_left = room.deposit,
    )
    alarm.alarm_to.coin -= room.deposit
    alarm.alarm_to.save()

    alarm.delete()
    return HttpResponse(status=204)

@login_required
def reject_request(request, alarm_id):
    alarm = get_object_or_404(Alarm, id=alarm_id)
    alarm.delete()
    return redirect('alarm:show_alarms')
