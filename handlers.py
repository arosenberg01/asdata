import logging
import sys
import json
import requests
import bs4
from sqlalchemy.orm import sessionmaker
from boto3 import client as boto3_client
from utilities import team_mappings
from models import create_tables, db_connect
from classes import NbaPlayerPage
from classes import NbaTeamPage

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

lambda_client = boto3_client('lambda')

def init_db_con():
    try:
        engine = db_connect()
        create_tables(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        logger.info('SUCCESS: Connection to mysql instance succeeded')

        return session
    except Exception as e:
        logger.error('ERROR: Could not connect to mysql instance.')
        logger.error(e)
        sys.exit()

### HANDLERS ###

# insert individual nba player games for all teams/players, all players on a team, or specific players
def update_player_games(event, context, session):
    to_update = []

    if 'team_ids' in event['args']:
        # update all games for all teams
        if event['args']['team_ids'][0] == 'all':
            event['args']['team_ids'] = team_mappings['abrv_city_to_abrv_full']

        # update games for players by team
        for team_id in event['args']['team_ids']:
            nba_team = NbaTeamPage(team_id, requests, bs4)

            for player_id in nba_team.player_ids:
                nba_player = NbaPlayerPage(player_id)
                nba_player.update_games(session)

    # update games for individual players
    elif 'player_ids' in event['args']:
        for player_id in event['args']['player_ids']:
            nba_player = NbaPlayerPage(player_id, requests, bs4)
            nba_player.get(nba_player.url)
            nba_player.convert(nba_player.html.text)
            print(nba_player.parse_games(nba_player.soup))

            # nba_player.update_games(session)

def update_roster(event, context, session):
    if event['args']['team_ids'][0] == 'all':
        event['args']['team_ids'] = team_mappings['abrv_city_to_abrv_full']

    for team_id in event['args']['team_ids']:
        nba_team = NbaTeamPage(team_id)
        nba_team.update_roster(session)

def update_teams(event, context, session):
    for team_id in team_mappings['abrv_city_to_abrv_full'].itervalues():
        team = NbaTeamPage(team_id)
        team.update_team(session)

def trigger_game_updates(event, context, session):
    for team_id in team_mappings['abrv_city_to_abrv_full'].itervalues():
        msg = {
            'handler_name': 'update_player_games',
            'args': {
                'team_ids': [team_id]
            }
        }

        print(team_id)

        lambda_client.invoke(FunctionName='BballScraper',
                             InvocationType='Event',
                             Payload=json.dumps(msg))

def trigger_roster_updates(event, context, session):
    for team_id in team_mappings['abrv_city_to_abrv_full'].itervalues():
        msg = {
            'handler_name': 'update_roster',
            'args': {
                'team_ids': [team_id]
            }
        }

        print(team_id)

        lambda_client.invoke(FunctionName='BballScraper',
                             InvocationType='Event',
                             Payload=json.dumps(msg))

def invalid_handler(event, context, session):
    logger.error('ERROR: handler "%s" not found', event['handler_name'])
    sys.exit()

#######

def handler_switch(handler):
    return {
        'update_player_games': update_player_games,
        'update_roster': update_roster,
        'update_teams': update_teams,
        'trigger_game_updates': trigger_game_updates,
        'trigger_roster_updates': trigger_roster_updates
    }.get(handler, invalid_handler)

def main(event, context):
    session = init_db_con()

    try:
        # update_teams(session)
        handler = handler_switch(event['handler_name'])
        handler(event, context, session)

        session.commit()
    except Exception as e:
        logger.error(e)
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    # for team_id in team_mappings['abrv_city_to_abrv_full'].itervalues():
        # main({
        #     'handler_name': 'update_roster',
        #     'args': {
        #         'team_ids': [team_id]
        #     }
        # }, {})
    # main({
    #     'handler_name': 'trigger_game_updates',
    #     'args': {
    #         'team_ids': []
    #     }
    # }, {})
    main({
        'handler_name': 'update_player_games',
        'args': {
            'player_ids': ['5601']
        }
    }, {})
    # main({
    #     'handler_name': 'trigger_game_updates',
    #     'args': {
    #         'team_ids': ['orl']
    #     }
    # }, {})