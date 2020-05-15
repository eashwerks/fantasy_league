from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

from app_0.models import IPLTeam, AuthUser, Player


@login_required
def index_view(request):
    template_name = 'app_0/index.html'
    context = {}

    if request.method == 'GET':
        l_board = AuthUser.objects.order_by('allocated_points')
        if not l_board.count() < 5:
            l_board = l_board[:5]
        context['l_board'] = l_board
        return render(request, template_name, context)


@login_required
def team_view(request):
    queryset = IPLTeam.objects.all().order_by('-name')
    context = {}
    template_name = 'app_0/teams.html'
    if request.method == 'GET':
        context['ipl_teams_1'] = queryset[:4]
        context['ipl_teams_2'] = queryset[4:]
        return render(request, template_name, context)


@login_required
def leader_board_view(request):
    template_name = 'app_0/leader_board.html'
    context = {}

    if request.method == 'GET':
        l_board = AuthUser.objects.order_by('allocated_points')
        if not l_board.count() < 5:
            l_board = l_board[:5]
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
        players = Player.objects.filter(team_players__team__created_by=user, team_players__is_active=True)

        context['players'] = players
        return render(request, template_name, context)


def start(request):
    if not request.user.is_authenticated:
        return redirect(login_view)
    return redirect(index_view)


def login_view(request):
    template_name = 'app_0/login.html'
    context = {}
    error_message = ''
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(start)
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
        return render(request, template_name, context)


def logout_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
    return redirect(start)
