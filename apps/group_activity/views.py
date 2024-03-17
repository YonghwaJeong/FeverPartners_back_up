from django.shortcuts import render, redirect, get_object_or_404
from apps.group_management.models import Room
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import AuthenticationForm, MemberAuthenticationForm
from apps.goal_management.models import Goal
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from apps.group_activity.models import UserActivityInfo
from django.db.models import Case, When, Value, IntegerField

#room 중복되는 건 추후에 제거 할 예정
def show_activity_main(request, room_id):
    room = Room.objects.get(pk=room_id)
    ctx = {
        'room_id':room_id,
        'room': room,
    }
    return render(request, 'group_activity/group_activity_base.html', ctx)

def activate(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    authentications = Authentication.objects.filter(room=room)
    ctx = {
        'room': room,
        'room_id': room.pk,
        'authentications': authentications,
        'current_time': timezone.now(),
    }
    return render(request, 'group_activity/group_activate.html', ctx)

#그룹장이 방에 인증 틀을 생성하는 것
def create_auth(request, room_id):
    if request.method == 'GET':
        form = AuthenticationForm()

        ctx = {
            'form': form,
            'room_id': room_id,
            }
        return render(request, 'group_activity/create_auth.html', ctx)

    # POST일때
    form = AuthenticationForm(request.POST)
    room = get_object_or_404(Room, id=room_id)
    
    form.instance.room = room
    form.instance.user = request.user
    form.save()

    return redirect('group_activity:main_page', room_id=room_id)

#그룹장이 올린 인증 틀에 멤버들이 인증을 생성하는 것
def create_authentication(request, room_id, auth_id):
    target_auth = get_object_or_404(Authentication, pk=auth_id)

    if request.method == 'GET':
        form = MemberAuthenticationForm()

        ctx = {
            'form': form,
            'room_id': room_id,
            'auth_id': auth_id,
            'auth': target_auth,
            }
        return render(request, 'group_activity/create_authentication.html', ctx)

    # POST일때
    form = MemberAuthenticationForm(request.POST, request.FILES)
    room = get_object_or_404(Room, id=room_id)
    target_auth.participated.add(request.user)
    form.instance.room = room
    form.instance.user = request.user
    form.save()

    return redirect('group_activity:main_page', room_id=room_id)

#그룹장이 인증확인 창으로 이동
@login_required
def verify(request, room_id):
    memberAuthentication = MemberAuthentication.objects.filter(room=room_id).filter(is_completed=False)
    room_id = room_id
    room = Room.objects.get(pk = room_id)
    ctx = {
        'memberAuthentication':memberAuthentication,
        'room_id':room_id,
        'room':room,
    }
    return render(request, 'group_activity/verifying_auth.html', ctx)

def load_auth_detail(request, auth_id):
    memberAuth = MemberAuthentication.objects.get(pk=auth_id)
    cnt = {
        'auth':memberAuth,
    }
    return render(request, 'group_administration/auth_detail.html', cnt)

#인증 수락을 눌렀을 때
def accept_auth_log(request, member_auth_id):
    memberAuthentication = MemberAuthentication.objects.get(id=member_auth_id)
    user =  memberAuthentication.user
    room = memberAuthentication.room
    user.fuel = add_fever(user.fuel)
    user.save()
    user_info = user.activity_infos.all().get(room=room)
    user_info.authentication_count += 1
    user_info.save()
    memberAuthentication.is_auth = True
    memberAuthentication.is_completed = True
    memberAuthentication.save()

    return HttpResponse(status=204)

#인증 거절을 눌렀을 때
def refuse_auth_log(request, member_auth_id):
    memberAuthentication = MemberAuthentication.objects.get(id=member_auth_id)
    user =  memberAuthentication.user
    room = memberAuthentication.room
    user.fuel = loss_fever(user.fuel)
    user.save()
    if room.cert_required:
        user_info = user.activity_infos.all().get(room=room)
        take_penalty(user_info, room, room.penalty_value)
    memberAuthentication.is_completed = True
    memberAuthentication.save()

    return HttpResponse(status=204)

@require_http_methods(["DELETE"])
def close_authentication(request, room_id, auth_id):
    try:
        room = Room.objects.get(pk=room_id)
        auth = Authentication.objects.get(pk=auth_id)
        if room.cert_required:
            participated_users = auth.participated.all()
            non_participated_members = room.members.exclude(pk__in=[user.pk for user in participated_users])
            for member in non_participated_members:
                member.fuel = loss_fever(member.fuel)
                member.save()
                user_info = member.activity_infos.all().get(room=room)
                take_penalty(user_info, room, room.penalty_value)
        auth.delete()
        return JsonResponse({'message': '인증이 성공적으로 삭제되었습니다.'}, status=200)
    except Exception:
        return HttpResponse(status=400)
    
def add_fever(fever):
    fever_after = 0
    if 0 <= fever <= 25:
        fever_after = fever + 5
    elif 25 < fever <= 50:
        fever_after = fever + 1
    elif 50 < fever <= 75:
        fever_after = fever + 0.5
    elif 75 < fever <= 100:
        fever_after = max(100, fever + 0.1)
    return fever_after

def loss_fever(fever):
    fever_after = 0
    if 0 <= fever <= 25:
        fever_after = max(0, fever - 1)
    elif 25 < fever <= 50:
        fever_after = fever - 3
    elif 50 < fever <= 75:
        fever_after = fever - 5
    elif 75 < fever <= 100:
        fever_after = fever - 10
    return fever_after

def take_penalty(user_info: UserActivityInfo, room: Room, penalty):
    if user_info.deposit_left < penalty:
        expel_from_room(room, user_info.user, user_info)
        room.penalty_bank += user_info.deposit_left
        room.save()
    else:
        user_info.deposit_left -= penalty
        user_info.save()
        room.penalty_bank += penalty
        room.save()

def expel_from_room(room: Room, user, user_info):
    goal = Goal.objects.filter(user=user).get(belonging_group_id=room.pk)
    goal.belonging_group_id = None
    goal.is_in_group = False
    goal.save()
    room.members.remove(user)
    user_info.delete()
    if user == room.master:
        new_master = room.activity_infos.all().order_by('-authentication_count').first().user
        room.master = new_master
        room.save()

#현황(인증로그) 창으로 이동
def show_log(request, room_id):
    room = Room.objects.get(pk=room_id)
    auth_log = MemberAuthentication.objects.filter(room=room).filter(is_completed=True).order_by('-created_date')
    ctx = {
        'auth_log':auth_log,
        'room_id':room_id,
        'room':room,
    }
    return render(request, 'group_activity/show_log.html', ctx)

def show_member_list(request, room_id):
    member_list = []
    room = Room.objects.get(id=room_id)
    members_ordered = room.members.annotate(
    is_master=Case(
        When(id=room.master_id, then=Value(0)),
        default=Value(1),
        output_field=IntegerField(),
    )).order_by('is_master')
    for member in members_ordered.all():
        target_goal = member.goal.all().get(belonging_group_id=room_id)
        target_user_info = member.activity_infos.get(room=room)
        member_list.append({'user':member, 'goal':target_goal, 'user_info':target_user_info})

    cnt = {
        'room_id': room_id,
        'member_list': member_list,
        'room': room,
    }

    return render(request, 'group_activity/member_list.html', cnt)

@require_http_methods(["POST"])
def permission_check(request):
    try:
        data = json.loads(request.body)
        room_id = data.get('roomId')
        user_id = data.get('userId')

        master = Room.objects.get(pk=room_id).master
        if master.pk != user_id:
            return HttpResponse(status=403)
        return HttpResponse(status=204)
    except Exception:
        return HttpResponse(status=400)

@require_http_methods(["POST"])
def withdraw_from_room(request):
    try:
        data = json.loads(request.body)
        room_id = data.get('roomId')
        user_id = data.get('userId')
        
        room = Room.objects.get(pk=room_id)
        master = room.master
        # 관리자는 바로 탈퇴 불가능
        if master.pk == user_id:
            return HttpResponse(status=403)
        
        target = room.members.get(pk=user_id)
        room.members.remove(target)

        # 자의적 탈퇴 => 보증금 환급 안함
        user_info= room.activity_infos.all().get(user=target)
        room.penalty_bank += user_info.deposit_left
        room.save()
        user_info.delete()

        #Goal을 리셋하는 작업
        target_goal = Goal.objects.filter(user__pk=user_id).get(belonging_group_id=room_id)
        target_goal.belonging_group_id = None
        target_goal.is_in_group = False
        target_goal.save()
        
        return JsonResponse({'message':'탈퇴처리가 성공적으로 완료되었습니다.'}, status=200)
    except Exception:
        return HttpResponse(status=400)
