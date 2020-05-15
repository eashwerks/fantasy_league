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

from app_0 import views

urlpatterns = [
    path('index/', views.index_view, name='index-view'),
    path('iplTeams/', views.team_view, name='team-view'),
    path('leaderBoard/', views.leader_board_view, name='leader-board-view'),
    path('myTeam/', views.my_team_view, name='my-team-view'),
    path('login/', views.login_view, name='login-view'),
    path('logout/', views.logout_view, name='logout-view'),

]
