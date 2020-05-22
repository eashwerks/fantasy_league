from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import render, redirect

# Create your views here.
from admin_1.models import Match, MatchPlayerMapping
from app_0.models import IPLTeam, Player


def admin_login_required(function=None, redirect_field_name='next', login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


@admin_login_required
def dash_board_view(request):
    template_name = 'admin_1/dashboard.html'
    return render(request, template_name)


@admin_login_required
def admin_team_view(request):
    template_name = 'admin_1/admin_team.html'
    error_message = ''
    teams = IPLTeam.objects.all()
    context = {}
    if request.method == 'GET':
        context['teams'] = teams
        return render(request, template_name, context)
    if request.method == 'POST':
        name = request.POST.get('teamName', '')
        image = request.FILES.get('teamPhoto', None)
        description = request.POST.get('teamDescription', '')
        try:
            if name and image and description:
                IPLTeam.objects.create(name=name, image=image, description=description)
            else:
                error_message = 'All fields are mandatory'
        except Exception as err:
            error_message = err
            context['name'] = name
            context['description'] = description
        context['error_message'] = error_message
        context['teams'] = teams
        return render(request, template_name, context)


@admin_login_required
def delete_team(request, pk):
    try:
        team = IPLTeam.objects.get(pk=pk)
    except:
        team = None
    if team:
        team.delete()
    return redirect(admin_team_view)


@admin_login_required
def player_team_view(request):
    template_name = 'admin_1/player_team.html'
    error_message = ''
    teams = IPLTeam.objects.annotate(player_count=Count('players'))
    context = {}
    if request.method == 'GET':
        context['teams'] = teams
        return render(request, template_name, context)


@admin_login_required
def admin_player_view(request, pk):
    template_name = 'admin_1/admin_player.html'
    error_message = ''
    team = IPLTeam.objects.get(pk=pk)
    players = Player.objects.filter(ipl_team=team)
    context = {}
    if request.method == 'GET':
        context['players'] = players
        context['team'] = team
        return render(request, template_name, context)
    if request.method == 'POST':
        name = request.POST.get('playerName', '')
        _id = request.POST.get('playerId', None)
        image = request.FILES.get('playerPhoto', None)
        capped = request.POST.get('capped', 'off')
        un_capped = request.POST.get('uncapped', 'off')
        category = request.POST.get('playerSpecialisation', None)
        is_capped = None
        if capped == 'on':
            is_capped = True
        elif un_capped == 'on':
            is_capped = False

        try:
            if name and image and category:
                name = name.split()
                if not _id:
                    print(is_capped)
                    Player.objects.create(first_name=name[0], last_name=' '.join(name[1:]), dp=image,
                                          is_capped=is_capped,
                                          ipl_team=team, category=category)
                else:
                    print(is_capped)
                    p = Player.objects.get(pk=int(_id))
                    p.first_name = name[0]
                    p.last_name = ' '.join(name[1:])
                    p.dp = image
                    p.is_capped = is_capped
                    p.ipl_team = team
                    p.category = category
                    p.save()
            else:
                error_message = 'All fields are mandatory'
        except Exception as err:
            error_message = err
            context['name'] = name
            context['capped'] = capped
            context['uncapped'] = un_capped

        context['error_message'] = error_message
        context['team'] = team
        context['players'] = players
        return render(request, template_name, context)


@admin_login_required
def admin_match_view(request):
    template_name = 'admin_1/match.html'
    error_message = ''
    teams = IPLTeam.objects.all()
    matches = Match.objects.all()
    context = {}
    if request.method == 'GET':
        context['teams'] = teams
        context['matches'] = matches
        return render(request, template_name, context)
    if request.method == 'POST':
        team_1 = request.POST.get('team1', None)
        team_2 = request.POST.get('team2', None)
        image = request.FILES.get('coverPhoto', None)
        date = request.POST.get('matchDate', None)
        try:
            if team_1 and team_2 and image and date:
                if team_1 == team_2:
                    raise Exception('Both are same team')
                team_1 = teams.get(pk=int(team_1))
                team_2 = teams.get(pk=int(team_2))
                Match.objects.create(team_1=team_1, team_2=team_2, cover=image, date=date)
            else:
                error_message = 'All fields are mandatory'
        except Exception as err:
            error_message = err
            context['date'] = date
        context['error_message'] = error_message
        context['teams'] = teams
        context['matches'] = matches
        return render(request, template_name, context)


@admin_login_required
def delete_match(request, pk):
    try:
        match = Match.objects.get(pk=pk)
    except:
        match = None
    if match:
        match.delete()
    return redirect(admin_match_view)


@admin_login_required
def admin_player_points(request, pk):
    template_name = 'admin_1/player_points.html'
    error_message = ''
    match = Match.objects.get(pk=pk)
    match_maps = MatchPlayerMapping.objects.filter(match=match)
    context = {}
    if request.method == 'GET':
        context['team_1'] = match.team_1
        context['team_2'] = match.team_2
        context['players_1'] = match_maps.filter(player__ipl_team=match.team_1)
        context['players_2'] = match_maps.filter(player__ipl_team=match.team_2)
        return render(request, template_name, context)
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                obj = match_maps.get(player=key)
                obj.score = int(value)
                obj.save()
        return redirect(admin_player_points, pk=pk)


@admin_login_required
def match_team_view(request):
    template_name = 'admin_1/match_team.html'
    error_message = ''
    matches = Match.objects.all()
    context = {}
    if request.method == 'GET':
        context['matches'] = matches
        return render(request, template_name, context)


@admin_login_required
def delete_player(request, pk):
    team = None
    try:
        player = Player.objects.get(pk=pk)
    except:
        player = None
    if player:
        team = player.ipl_team
        player.delete()
    return redirect(admin_player_view, pk=team.id)
