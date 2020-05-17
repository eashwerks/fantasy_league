from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import render, redirect

# Create your views here.
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
        image = request.FILES.get('playerPhoto', None)
        capped = request.POST.get('capped', 'off')
        un_capped = request.POST.get('uncapped', 'off')
        category = request.POST.get('playerSpecialisation', None)

        if capped == 'on':
            is_capped = True
        if un_capped == 'on':
            is_capped = False

        try:
            if name and image and category:
                name = name.split()

                Player.objects.create(first_name=name[0], last_name=' '.join(name[1:]), dp=image, is_capped=is_capped,
                                      ipl_team=team)
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
