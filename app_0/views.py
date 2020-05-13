from django.http import HttpResponse
from django.shortcuts import render, redirect

from app_0.models import IPLTeam, AuthUser, Player


def index_view(request):
    template_name = 'app_0/index.html'
    context = {}

    if request.method == 'GET':
        l_board = AuthUser.objects.order_by('allocated_points')
        if not l_board.count() < 5:
            l_board = l_board[:5]
        context['l_board'] = l_board
        return render(request, template_name, context)


def team_view(request):
    queryset = IPLTeam.objects.all().order_by('-name')
    context = {}
    template_name = 'app_0/teams.html'
    if request.method == 'GET':
        context['ipl_teams_1'] = queryset[:4]
        context['ipl_teams_2'] = queryset[4:]
        return render(request, template_name, context)


def leader_board_view(request):
    template_name = 'app_0/leader_board.html'
    context = {}

    if request.method == 'GET':
        l_board = AuthUser.objects.order_by('allocated_points')
        if not l_board.count() < 5:
            l_board = l_board[:5]
        context['l_board'] = l_board
        return render(request, template_name, context)


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
    return redirect(index_view)
