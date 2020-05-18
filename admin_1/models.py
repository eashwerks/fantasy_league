from django.db import models, transaction

from app_0.models import IPLTeam, Player, TeamPlayerMappings


class Match(models.Model):
    team_1 = models.ForeignKey(IPLTeam, on_delete=models.CASCADE, related_name='team_2')
    team_2 = models.ForeignKey(IPLTeam, on_delete=models.CASCADE, related_name='team_1')
    date = models.DateField(auto_now=True)
    cover = models.ImageField(upload_to='mach_covers/')

    def __str__(self):
        return '{} vs {}'.format(self.team_1.name, self.team_2.name)

    class Meta:
        default_related_name = 'matches'

    @transaction.atomic
    def save(self, **kwargs):
        if not self.id:
            super(Match, self).save(**kwargs)
            self._map_players()
        else:
            super(Match, self).save(**kwargs)

    def _map_players(self):
        for item in self.team_1.players.all():
            MatchPlayerMapping.objects.create(player=item, match=self)
        for item in self.team_2.players.all():
            MatchPlayerMapping.objects.create(player=item, match=self)


class MatchPlayerMapping(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return '{} on {}'.format(self.player.full_name, self.match)

    class Meta:
        default_related_name = 'match_player_mappings'

    @transaction.atomic
    def save(self, **kwargs):
        if self.id:
            items = TeamPlayerMappings.objects.filter(player=self.player, is_active=True)
            for item in items:
                score = self.score
                if item.is_caption:
                    score = 5 * score
                if item.is_vise_caption:
                    score = 3 * score
                if item.is_power_player:
                    score = 2 * score
                item.points = item.points + score
                item.save()
        super(MatchPlayerMapping, self).save(**kwargs)
