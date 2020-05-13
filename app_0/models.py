import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models, transaction

from model_utils import Choices
from model_utils.fields import StatusField


class AuthUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model which is root of all corporate, yard and survey users.
    Type of user will be defined here.
    """
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=32, unique=True)
    phone_number = models.CharField(max_length=24)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32, null=True, blank=True)

    dp = models.FileField(upload_to='profile_picture', null=True, blank=True)

    allocated_points = models.IntegerField(default=120)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'phone_number']

    def __str__(self):
        return self.username


class IPLTeam(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to='team_images/')

    def __str__(self):
        return self.name


class Player(models.Model):
    CATEGORY = Choices('BATSMEN', 'BOWLERS', 'WICKET_KEEPERS', 'ALL_ROUNDERS')

    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32, null=True, blank=True)
    category = StatusField(choices_name='CATEGORY')
    is_capped = models.BooleanField(default=False)
    is_team_active = models.BooleanField(default=False)
    ipl_team = models.ForeignKey(IPLTeam, on_delete=models.CASCADE)

    dp = models.ImageField(upload_to='player_images', null=True, blank=True)

    points = models.IntegerField(default=0)

    class Meta:
        default_related_name = 'players'

    def __str__(self):
        return self.last_name

    def save(self, **kwargs):
        if self.is_capped:
            if self.category in ('BATSMEN', 'BOWLERS'):
                self.points = 9
            if self.category in ('WICKET_KEEPERS', 'ALL_ROUNDERS'):
                self.points = 8
        else:
            if self.category is not 'WICKET_KEEPERS':
                self.points = 7
            else:
                self.points = 8
        return super(Player, self).save(**kwargs)


class Team(models.Model):
    name = models.UUIDField(default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TeamPlayerMappings(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        default_related_name = 'team_players'

    def __str__(self):
        return '{} of {}'.format(self.player.name, self.team.name)

    @transaction.atomic
    def save(self, **kwargs):
        if not self.id:
            previous_team = self.model.objects.filter(player=self.player, is_active=True).last()
            if previous_team:
                previous_team.is_active = False
                previous_team.save()
        self._update_points()
        self._update_player_status()
        return super(TeamPlayerMappings, self).save(**kwargs)

    def _update_points(self):
        if self.is_active:
            updating_points = self.team.created_by.allocated_points - self.player.points
            if updating_points >= 0:
                self.team.created_by.allocated_points = updating_points
                self.team.created_by.save()
            else:
                raise Exception('Insufficient points')
        if not self.is_active:
            self.team.created_by.allocated_points = self.team.created_by.allocated_points + self.player.points
            self.team.created_by.save()

    def _update_player_status(self):
        player = self.player
        if self.is_active:
            player.is_team_active = True
        if not self.is_active:
            player.is_team_active = False
        player.save()
