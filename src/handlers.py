import logging
import sys
from sqlalchemy.orm import sessionmaker
from db.models.model import create_tables, db_connect
from classes.NbaPlayerPage import NbaPlayerPage
from classes.NbaTeamPage import NbaTeamPage
from utilities import team_mappings
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

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

def update_player_games(event, context, session):
    for team_id in event['args']['team_ids']:
        nba_team = NbaTeamPage(team_id)

        for player_id in nba_team.player_ids:
            nba_player = NbaPlayerPage(player_id)
            nba_player.update_games(session)

    # for player_id in event['args']['player_ids']:
    #     nba_player = NbaPlayerPage(player_id)
    #     nba_player.update_games(session)

def update_roster(event, context, session):
    for team_id in event['args']['team_ids']:
        nba_team = NbaTeamPage(team_id)
        nba_team.update_roster(session)


def update_schedule():
    return

def update_teams(session):
    for team_id in team_mappings['abrv_city_to_abrv_full'].itervalues():
        team = NbaTeamPage(team_id)
        team.update_team(session)

def invalid_handler(event, context, session):
    logger.error('ERROR: handler "%s" not found', event['handler_name'])
    sys.exit()
###


def handler_switch(handler):
    return {
        'update_player_games': update_player_games,
        'update_roster': update_roster,
        'update_schedule': update_schedule
    }.get(handler, invalid_handler)

def main(event, context):


    start = time.time()


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

        end = time.time()
        print(end - start)
        session.close()



if __name__ == "__main__":
    # main({
    #     'handler_name': 'update_player_games',
    #     'args': {
    #         'player_ids': ['4750', '4942']
    #     }
    # }, {})
    main({
        'handler_name': 'update_player_games',
        'args': {
            'team_ids': ['atl']
        }
    }, {})
    # main({
    #     'handler_name': 'update_roster',
    #     'args': {
    #         'team_ids': ['atl']
    #     }
    # }, {})
    # main(['4750', '4942'])
    # nba_player = NbaPlayer('4942')

