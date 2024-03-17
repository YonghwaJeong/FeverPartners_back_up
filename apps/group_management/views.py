from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from apps.goal_management.models import Goal
from apps.alarm.models import Alarm
from apps.group_management.models import Room 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponse
from django.urls import reverse
from elasticsearch_dsl import Search, Q
from apps.group_administration.decorators import room_admin_required
from django.views.decorators.http import require_http_methods
import json
from apps.group_activity.models import UserActivityInfo
from django.utils import timezone
import isodate

def start_creation(request):
    goals = Goal.objects.filter(user = request.user).filter(is_in_group = False).filter(is_completed = False)
    cnt = {
        'goals':goals
    }
    return render(request, 'group_management/group_creation.html', cnt)

@login_required
def create_room(request):
    if request.method == 'POST':
        goal_id = request.POST.get('goal')
        title = request.POST.get('title')
        detail = request.POST.get('detail')
        cert_required = request.POST.get('cert_required')
        cert_detail = request.POST.get('cert_detail', '')
        penalty = request.POST.get('penalty', 0)
        duration = request.POST.get('room-duration')
        favor_offline_str = request.POST.get('favor_offline', 'False')
        favor_offline = favor_offline_str == 'True'
        deposit = request.POST.get('deposit', 0)
        penalty = int(penalty) if penalty else 0
        deposit = int(deposit) if deposit else 0
        print(duration)

        # 서버사이드 validation
        # if not goal_id or not title or not detail:
        #     return redirect('your_redirect_url')

        my_goal = get_object_or_404(Goal, pk=goal_id)

        room = Room.objects.create(
            title = title,
            detail = detail,
            master=request.user,
            cert_required = bool(cert_required),
            favor_offline = favor_offline,
            duration = isodate.parse_duration(duration),
            deposit = deposit,
        )

        if bool(cert_required):
            room.cert_detail = cert_detail
            room.penalty_value = penalty
        
        # 일단은 master도 member로 추가, 혹시 문제가 되면 수정
        room.members.add(request.user)
        room.tags.set(my_goal.tags.all())
        room.activityTags.set(my_goal.activityTags.all())
        room.save()
        
        my_goal.is_in_group = True
        my_goal.belonging_group_id = room.id
        my_goal.save()

        # 활동정보 인스턴스 추가, 코인 징수
        UserActivityInfo.objects.create(
            user = request.user,
            room = room,
            deposit_left = int(deposit),
        )
        request.user.coin -= int(deposit)
        request.user.save()

        url = reverse('group_management:recommendation_page', kwargs={'room_id': room.pk})
        return redirect(url)
    
    else:
        return HttpResponseBadRequest('잘못된 접근방식입니다.')
    
# 임시로 작성해둠
def show_user_list(request):
    return render(request, 'group_management/member_recom.html')

@room_admin_required
def recommend_member(request, room_id):
    room = Room.objects.get(pk=room_id)
    tag_ids = [tag.id for tag in room.tags.all()]
    activity_tags_ids = [tag.id for tag in room.activityTags.all()]
    alarms = Alarm.objects.filter(room__pk=room_id).exclude(goal=None)
    is_pending = [alarm.goal.pk for alarm in alarms]

    must_queries = []
    should_queries = []
    must_not_queries = []

    # 최소조건 명시 : 분류 태그 중 하나는 같아야 함(사실 이는 원시태그로 한정되긴 함)
    # group에 가입되지 않은 목표여야 함 
    at_least = Q('nested', path='tags', query=Q('terms', **{'tags.tag_id': tag_ids}), boost=0)
    in_group_check_query = Q('term', is_in_group = False)
    # 아직 완료되지 않은 목표여야 함
    is_completed_query = Q('term', is_completed=False)
    must_queries.append(at_least)
    must_queries.append(in_group_check_query)
    must_queries.append(is_completed_query)

    # 가중 조건 : 검색결과에 점수를 추가적으로 부여하는 로직들
    for tag_id in tag_ids:
        tag_query = Q('nested', path='tags', query=Q('terms', **{'tags.tag_id': [tag_id]}), boost=3)
        should_queries.append(tag_query)

    for activity_tag_id in activity_tags_ids:
        activity_tag_query = Q('nested', path='activityTags', query=Q('terms', **{'activityTags.tag_id': [activity_tag_id]}), boost=3)
        should_queries.append(activity_tag_query)

    offline_boost_query = Q('term', favor_offline={'value': room.favor_offline, 'boost': 2})
    should_queries.append(offline_boost_query)

    if room.favor_offline:
        region_boost_query = Q('match', user__region={'query': room.master.region, 'boost': 2})
        detail_boost_query = Q('match', user__region_detail={'query': room.master.region_detail, 'boost': 2})
        should_queries.append(region_boost_query)
        should_queries.append(detail_boost_query)

    title_boost_query = Q('match', title={'query': room.title, 'boost': 2})
    content_boost_query = Q('match', content={'query': room.detail, 'boost': 2})
    should_queries.append(title_boost_query)
    should_queries.append(content_boost_query)

    master_detecting_query = Q('term', **{'user.id': room.master.pk})
    must_not_queries.append(master_detecting_query)

    final_query = Q('bool', must=must_queries, should=should_queries, must_not=must_not_queries)
    
    s = Search(index='goals').query(final_query)
    s = s.sort({'_score': {'order': 'desc'}})
    response = s.execute()
    hit_scores = {hit.meta.id: hit.meta.score for hit in response if hit.meta.id not in is_pending}
    print(hit_scores)
    goals = sorted(Goal.objects.filter(pk__in=hit_scores.keys()), key=lambda goal: hit_scores[str(goal.pk)], reverse=True)
    cnt = {
        'goals' : goals,
        'room' : room
    }
    return render(request, 'group_management/member_recom.html', cnt)

@room_admin_required
@require_http_methods(["POST"])
def suggest_join(request, room_id):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        goal_id = data.get('goal_id')
        user = get_object_or_404(get_user_model(), id=user_id)
        room = get_object_or_404(Room, id=room_id)
        goal = get_object_or_404(Goal, id=goal_id)
        Alarm.objects.create(alarm_from=request.user, alarm_to=user, room = room, goal = goal)
        return HttpResponse(status=204)
    except Exception:
        return HttpResponse(status=400)
    
def show_group_list(request):
    user = request.user
    rooms = Room.objects.filter(members__in = [user])
    return render(request, 'group_management/group_list.html', {'rooms': rooms, 'current_time': timezone.localtime()})

def check_user_goal(request):
    available_goals = Goal.objects.filter(user=request.user).exclude(is_completed=True).exclude(is_in_group=True)
    if available_goals:
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=400)
    
def check_room_status(request, room_id):
    room = Room.objects.get(pk=room_id)
    if room.is_active:
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=400)