"""
To upload agent details
Map agent to area and location
"""
import pandas as pd

from django.db import transaction

from app_0.models import Player


def upload_players():
    """
    To upload agent details
    """
    print("Uploading Players...")
    df = pd.read_csv('_temp/db_files/players.csv')
    df = df.fillna('')
    lst_columns = [columns.strip().replace(' ', '_').lower() for columns in df.columns if columns]
    df.columns = lst_columns

    for key, value in df.iterrows():
        first_name = value.first_name
        last_name = value.last_name
        category = value.specialism
        capped = True if value.c_a_u == 'Capped' else False

        player, created = Player.objects.get_or_create(first_name=first_name, last_name=last_name, category=category,
                                                       is_capped=capped)
        print('>>> {} {}'.format(player.full_name, 'CREATED' if created else 'Already EXIST'))


@transaction.atomic
def run():
    upload_players()
