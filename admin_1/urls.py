"""
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from admin_1 import views

urlpatterns = [
    path('dashBoard/', views.dash_board_view, name='dash-board-view'),
    path('teams/', views.admin_team_view, name='admin-team-view'),
    path('deleteTeam/<int:pk>/', views.delete_team, name='delete-team'),
    path('playerTeams/', views.player_team_view, name='player-team-view'),
    path('players/<int:pk>/', views.admin_player_view, name='admin-player-view'),
]
