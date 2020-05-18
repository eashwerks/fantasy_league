import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models, transaction

from model_utils import Choices
from model_utils.fields import StatusField

from app_0.managers import AuthUserManager


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
    is_staff = models.BooleanField(default=False)

    dp = models.FileField(upload_to='profile_picture', null=True, blank=True)

    allocated_points = models.IntegerField(default=120)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'phone_number']

    objects = AuthUserManager()

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        if self.last_name:
            return '{} {}'.format(self.first_name, self.last_name)
        return self.first_name

    def points(self):
        team = self.teams.last()
        if team:
            return sum(team.team_players.filter(is_active=True).values_list('points', flat=True))
        else:
            return 0

    @transaction.atomic
    def save(self, **kwargs):
        if not self.id:
            super(AuthUser, self).save(**kwargs)
            Team.objects.create(created_by=self)
        else:
            super(AuthUser, self).save(**kwargs)


class IPLTeam(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to='team_images/')
    description = models.TextField()

    def __str__(self):
        return self.name


class Player(models.Model):
    CATEGORY = Choices('BATSMEN', 'BOWLERS', 'WICKET_KEEPERS', 'ALL_ROUNDERS')

    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32, null=True, blank=True)
    category = StatusField(choices_name='CATEGORY')
    is_capped = models.BooleanField(default=False)
    ipl_team = models.ForeignKey(IPLTeam, on_delete=models.CASCADE, null=True, blank=True)

    dp = models.ImageField(upload_to='player_images', null=True, blank=True)

    points = models.IntegerField(default=0)

    class Meta:
        default_related_name = 'players'

    def __str__(self):
        return self.last_name

    @property
    def full_name(self):
        if self.last_name:
            return '{} {}'.format(self.first_name, self.last_name)
        return self.first_name

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
    batsmen = models.IntegerField(default=0)
    bowler = models.IntegerField(default=0)
    w_keeper = models.IntegerField(default=0)
    all_rounder = models.IntegerField(default=0)
    un_capped = models.IntegerField(default=0)
    set_caption = models.BooleanField(default=False)
    set_vise_caption = models.BooleanField(default=False)
    set_power_player = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        default_related_name = 'teams'

    def save(self, **kwargs):
        if not self.is_active:
            self._deactivate_players()
        return super(Team, self).save(**kwargs)

    def _deactivate_players(self):
        for item in self.team_players.all():
            item.is_active = False
            item.save()


class TeamPlayerMappings(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    is_caption = models.BooleanField(default=False)
    is_vise_caption = models.BooleanField(default=False)
    is_power_player = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        default_related_name = 'team_players'

    def __str__(self):
        return '{} of {}'.format(self.player.last_name, self.team.name)

    @transaction.atomic
    def save(self, **kwargs):
        if not self.id:
            self._update_points()
            self._update_count()
        self._validate_max_rules(True)
        self._activate_team()
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

    def _validate_max_rules(self, raise_exception=False):
        error = []
        if self.player.category in ['BATSMEN', 'BOWLERS']:
            if not (self.team.batsmen <= 5):
                error.append('No more capped {} can be added.'.format(self.player.category))
        if self.player.category == 'WICKET_KEEPERS':
            if not (self.team.w_keeper <= 2):
                error.append('No more {} can be added.'.format(self.player.category))
        if self.player.category == 'ALL_ROUNDERS':
            if not (self.team.all_rounder <= 2):
                error.append('No more capped {} can be added.'.format(self.player.category))
        if error:
            if raise_exception:
                raise Exception(','.join(error))
            return False
        return True

    def _activate_team(self):
        is_validated = True
        if not self.team.batsmen >= 3:
            is_validated = False
        if not self.team.bowler >= 3:
            is_validated = False
        if not self.team.w_keeper >= 1:
            is_validated = False
        if not self.team.all_rounder >= 1:
            is_validated = False
        if not self.team.un_capped >= 3:
            is_validated = False
        self.team.is_active = is_validated

    def _update_count(self):
        if self.player.category == 'BATSMEN':
            if self.player.is_capped:
                self.team.batsmen += 1
            else:
                self.team.un_capped += 1
        if self.player.category == 'BOWLERS':
            if self.player.is_capped:
                self.team.bowler += 1
            else:
                self.team.un_capped += 1
        if self.player.category == 'WICKET_KEEPERS':
            self.team.w_keeper += 1
            if not self.player.is_capped:
                self.team.un_capped += 1

        if self.player.category == 'ALL_ROUNDERS':
            if self.player.is_capped:
                self.team.bowler += 1
            else:
                self.team.un_capped += 1
