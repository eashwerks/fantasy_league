from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

from admin_1.models import Match
from admin_1.views import dash_board_view
from app_0.models import IPLTeam, AuthUser, Player, TeamPlayerMappings


@login_required
def index_view(request):
    template_name = 'app_0/index.html'
    context = {}

    if request.method == 'GET':
        l_board = AuthUser.objects.all()
        matches = Match.objects.all()
        if matches.count() < 3:
            context['matches'] = matches
        else:
            context['matches'] = matches[:3]
        context['l_board'] = l_board
        return render(request, template_name, context)


@login_required
def team_view(request):
    queryset = IPLTeam.objects.all().order_by('-name')
    context = {}
    template_name = 'app_0/teams.html'
    if request.method == 'GET':
        count = queryset.count() / 2
        context['ipl_teams_1'] = queryset[:count]
        context['ipl_teams_2'] = queryset[count:]
        return render(request, template_name, context)


@login_required
def leader_board_view(request):
    template_name = 'app_0/leader_board.html'
    context = {}

    if request.method == 'GET':
        l_board = AuthUser.objects.all()
        context['l_board'] = l_board
        return render(request, template_name, context)


@login_required
def my_team_view(request):
    template_name = 'app_0/my_team.html'
    context = {}

    if request.method == 'GET':
        user = request.user
        if not user:
            raise Exception('Not logged in')
        players = TeamPlayerMappings.objects.filter()

        context['players'] = players
        return render(request, template_name, context)


def select_player_view(request, pk):
    template_name = 'app_0/select_players.html'
    players = Player.objects.filter(ipl_team=pk)
    team = IPLTeam.objects.get(pk=pk)
    my_players = request.user.teams.last().team_players.values_list('player', flat=True)
    players = players.exclude(id__in=my_players)
    context = {}
    if request.method == 'GET':
        count = players.count()
        if count > 5:
            context['players_1'] = players[:count]
            context['players_2'] = players[count:]
        else:
            context['players_1'] = players
            context['team'] = team
        return render(request, template_name, context)


def add_to_team(request, pk):
    err_message = None
    player = Player.objects.get(pk=pk)
    try:
        team = request.user.teams.last()
        TeamPlayerMappings.objects.create(team=team, player=player)
    except Exception as err:
        err_message = err
    return redirect(select_player_view, player.ipl_team.id)


def start(request):
    if not request.user.is_authenticated:
        return redirect(login_view)
    if request.user.is_staff:
        return redirect(dash_board_view)
    return redirect(index_view)


def login_view(request):
    template_name = 'app_0/login.html'
    context = {}
    error_message = ''
    _type = 'login'
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(start)
        context['type'] = _type
        return render(request, template_name, context)
    if request.method == 'POST':
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        try:
            if email and password:
                user = authenticate(username=email, password=password)
                if user is not None:
                    login(request, user)
                    return redirect(start)
                else:
                    error_message = 'Check username and password'

            else:
                error_message = 'username and password required'
        except:
            error_message = 'Check username and password'

        context['email'] = email
        context['password'] = password
        context['error_message'] = error_message
        context['type'] = _type
        return render(request, template_name, context)


def logout_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
    return redirect(start)


def register_view(request):
    template_name = 'app_0/register.html'
    context = {}
    error_message = ''
    _type = 'register'
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(start)
        context['type'] = _type
        return render(request, template_name, context)
    if request.method == 'POST':
        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        email = request.POST.get('email', None)
        phone = request.POST.get('phone', None)
        password = request.POST.get('password', None)

        try:
            if email and password and first_name and phone:
                user = AuthUser.objects.create_user(email, phone, first_name, email, password)
                if last_name:
                    user.last_name = last_name
                    user.save()
                login(request, user)
                return redirect(start)
            else:
                error_message = 'All fields except Surname required'
        except Exception as err:
            error_message = err

        context['first_name'] = first_name
        context['last_name'] = last_name
        context['email'] = email
        context['phone'] = phone
        context['password'] = password
        context['error_message'] = error_message
        context['type'] = _type
        return render(request, template_name, context)
