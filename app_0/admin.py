from django.contrib import admin

from app_0.models import IPLTeam, AuthUser, Team, Player, TeamPlayerMappings

admin.site.register(IPLTeam)
admin.site.register(AuthUser)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(TeamPlayerMappings)
