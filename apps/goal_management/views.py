from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, HttpResponseBadRequest
from apps.alarm.models import Alarm
from .models import *
from django.contrib.auth.decorators import login_required
from elasticsearch_dsl import Search, Q
from apps.group_management.models import Room
from django.views.decorators.http import require_http_methods
from .decorators import goal_ownership_required
import json

def start_creation(request):
    tags = Tag.objects.filter(parent_tag__isnull=True).order_by('tag_name')
    actTags = ActivityTag.objects.all()
    cnt = {
        'tags':tags,
        'actTags':actTags,
    }
    return render(request, 'goal_management/goal_creation.html', cnt)

def get_subtags(request, id):
    subtags = Tag.objects.filter(parent_tag__id = id)
    cnt = {
        'subtags':subtags
    }
    html_content = render(request, 'goal_management/subtag_container.html', cnt).content
    return JsonResponse({'result':html_content.decode('utf-8')})

def show_branching_point(request):
    # 해당 페이지에 직접 접근하는 경우/goal_id가 없기 때문에 페이지 로딩X -> 예외처리
    return HttpResponseNotFound('잘못된 접근 방식입니다.')

@login_required
def create_goal(request):
    if request.method == 'POST':
        selected_tag_id = request.POST.get('selected_tag')
        activity_type_ids = request.POST.getlist('activity-type[]')
        title = request.POST.get('goal-title')
        details = request.POST.get('goal-details')
        meeting_preference = request.POST.get('meeting-preference')
        
        try:
            selected_subtag_id = request.POST.get('selected_subtag')
        except (ValueError, TypeError):
            selected_subtag_id = None

        # 서버사이드 validation => 추후에 수정
        # if not selected_tag_id or not activity_type_ids or not title or not details or not meeting_preference:
        #     return redirect('your_redirect_url')

        selected_tag = Tag.objects.get(id=selected_tag_id)
        activity_tags = ActivityTag.objects.filter(id__in=activity_type_ids)
        favor_offline = True if meeting_preference == 'True' else False

        goal = Goal.objects.create(
            user=request.user,
            title=title,
            content=details,
            favor_offline=favor_offline
        )

        goal.tags.add(selected_tag)
        goal.activityTags.set(activity_tags)

        if selected_subtag_id:
            selected_subtag = Tag.objects.get(id=selected_subtag_id)
            goal.tags.add(selected_subtag)

        return render(request, 'goal_management/branching_point.html', {'goal_id':goal.pk})
    
    # GET 요청으로 접근한 경우 예외처리 추후에 추가
    # return redirect()

@login_required
def goal_list(request):
    user = request.user
    goals = user.goal.all().order_by('is_completed')
    ctx = {
        "goals": goals,
    }
    return render(request, "goal_management/goal_list.html", ctx)

# 사용자의 목표 수정
def goal_update(request, pk):
    goal = Goal.objects.get(id=pk)
    tags = Tag.objects.filter(parent_tag__isnull=True).order_by('tag_name')
    actTags = ActivityTag.objects.all()
    ctx = {
        "goal": goal,
        "pk": pk,
        'tags':tags,
        'actTags':actTags,
    }
    return render(request, "goal_management/goal_update.html", ctx)

@require_http_methods(["DELETE"])
def delete_goal(request, goal_id):
    try:
        target = Goal.objects.get(pk=goal_id)
        target.delete()
        return JsonResponse({'message': '목표가 성공적으로 삭제되었습니다.'}, status=200)
    except Exception:
        return HttpResponse(status=400)

@goal_ownership_required
def recommend_group(request, goal_id):

    goal = Goal.objects.get(pk=goal_id)
    tag_ids = [tag.id for tag in goal.tags.all()]
    activity_tag_ids = [tag.id for tag in goal.activityTags.all()]
    alarms = Alarm.objects.filter(goal__pk=goal_id)
    is_pending = [alarm.room.pk for alarm in alarms]

    must_queries = []
    should_queries = []
    must_not_queries = []

    # 최소조건 명시: 분류 태그 중 하나는 같아야 함
    at_least_tag = Q('nested', path='tags', query=Q('terms', **{'tags.tag_id': tag_ids}), boost=0)
    must_queries.append(at_least_tag)

    # 가중 조건: 검색결과에 점수를 추가적으로 부여하는 로직들
    for tag_id in tag_ids:
        tag_query = Q('nested', path='tags', query=Q('terms', **{'tags.tag_id': [tag_id]}), boost=3)
        should_queries.append(tag_query)

    for activity_tag_id in activity_tag_ids:
        activity_tag_query = Q('nested', path='activityTags', query=Q('terms', **{'activityTags.tag_id': [activity_tag_id]}), boost=3)
        should_queries.append(activity_tag_query)

    # favor_offline이 같을 경우 높은 점수
    offline_boost_query = Q('term', favor_offline={'value': goal.favor_offline, 'boost': 2})
    should_queries.append(offline_boost_query)
    
    if goal.favor_offline:
        region_boost_query = Q('match', master__region={'query': goal.user.region, 'boost': 2})
        detail_boost_query = Q('match', master__region_detail={'query': goal.user.region_detail, 'boost': 2})
        should_queries.append(region_boost_query)
        should_queries.append(detail_boost_query)

    title_boost_query = Q('match', title={'query': goal.title, 'boost': 2})
    content_boost_query = Q('match', detail={'query': goal.content, 'boost': 2})
    should_queries.append(title_boost_query)
    should_queries.append(content_boost_query)

    # is_active가 False일때만 추천 목록에 반영 
    is_active_query = Q('term', is_active=False)
    must_queries.append(is_active_query)

    # Goal의 user는 Room의 master가 아니여야함. 즉 자기자신이 개설한 방에 대해서는 목록에 반영하지 않음.
    # => 상식적으로 이럴 일은 없겠으나, 일단 예외처리함
    user_master_mismatch_query = Q('term', master__id=goal.user.id)
    must_not_queries.append(user_master_mismatch_query)

    final_query = Q('bool', must=must_queries, should=should_queries, must_not=must_not_queries)
    s = Search(index='rooms').query(final_query)
    s = s.sort({'_score': {'order': 'desc'}})
    response = s.execute()
    hit_scores = {hit.meta.id : hit.meta.score for hit in response if hit.meta.id not in is_pending}
    rooms = sorted(Room.objects.filter(pk__in=hit_scores.keys()), key=lambda room: hit_scores[str(room.pk)], reverse=True)
    cnt = {
        'rooms': rooms,
        'goal': goal
    }
    return render(request, 'goal_management/group_recom.html', cnt)

@goal_ownership_required
@require_http_methods(["POST"])
def suggest_join(request, goal_id):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        room_id = data.get('room_id')
        user = get_object_or_404(get_user_model(), id=user_id)
        goal = get_object_or_404(Goal, id=goal_id)
        room = get_object_or_404(Room, id=room_id)
        Alarm.objects.create(alarm_from=request.user, alarm_to=user, goal = goal, room = room)
        return HttpResponse(status=204)
    except Exception:
        return HttpResponse(status=400)

def show_achievement_report_list(request):
    reports = AchievementReport.objects.all().order_by('-id')  # id는 보고서가 생성된 순서를 나타내는 것으로 가정합니다.
    cnt = {
        'reports': reports, 
    }
    return render(request, 'goal_management/achievement_report_main.html', cnt)

def show_achievement_report_detail(request, achievement_id):
    report = AchievementReport.objects.get(pk=achievement_id)
    cnt = {
        'report':report,
    }
    return render(request, 'goal_management/achievement_report_detail.html', cnt)

# 접속자의 Goal이 아닌 경우 GET 요청까지 차단
@goal_ownership_required
def create_achievement_report(request, goal_id):
    if request.method == "POST":
        content = request.POST.get('content')
        image = request.FILES.get('image')
        try:
            goal = Goal.objects.get(pk=goal_id)
            AchievementReport.objects.create(goal=goal, content=content, image=image)
            goal.is_completed = True
            goal.save()
            return HttpResponse(status=204)
        except Exception:
            return HttpResponse(status=400)
    else:
        goal = Goal.objects.get(pk=goal_id)
        if goal.is_completed:
            return HttpResponseBadRequest('이미 보고가 작성된 목표입니다.')
        cnt = {
            'goal':goal,
        }
        return render(request, 'goal_management/achievement_reporting_form.html', cnt)
    
def update_react_count(request, report_id):
    json_data = json.loads(request.body)
    report = AchievementReport.objects.get(pk=report_id)
    action = json_data.get('action')
    if action == 'love':
        love_count = report.reacted_love.count()
        if request.user in report.reacted_love.all():
            love_count -= 1
            report.reacted_love.remove(request.user)
        else:
            love_count += 1
            report.reacted_love.add(request.user)
        return JsonResponse({'love_count':love_count}, status=200)
    elif action == 'like':
        like_count = report.reacted_respectful.count()
        if request.user in report.reacted_respectful.all():
            like_count -= 1
            report.reacted_respectful.remove(request.user)
        else:
            like_count += 1
            report.reacted_respectful.add(request.user)
        return JsonResponse({'like_count':like_count}, status=200)
    elif action == 'dislike':
        dislike_count = report.reacted_dislike.count()
        if request.user in report.reacted_dislike.all():
            dislike_count -= 1
            report.reacted_dislike.remove(request.user)
        else:
            dislike_count += 1
            report.reacted_dislike.add(request.user)
        return JsonResponse({'dislike_count':dislike_count}, status=200)