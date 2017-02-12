import logging
import sys
from sqlalchemy.orm import sessionmaker
from models import NbaGame, NbaPlayer, create_tables, db_connect
# from classes/NbaPlayerPage import NbaScheduleSheet, NbaPlayerPage

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

def init_db_con():
    try:
        engine = db_connect()
        create_tables(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        logger.info('SUCCESS: Connection to mysql instance succeeded')

        return session
    except:
        logger.error('ERROR: Unexpected error: Could not connect to mysql instance.')
        sys.exit()

def update_player_games(event, context, session):
    for yahoo_id in event['yahoo_ids']:
        nba_player = NbaPlayerPage(yahoo_id)
        nba_player.update_player_info(session)
        nba_player.update_games(session)

def update_schedule():
    return

def invalid_handler(event, context, session):
    logger.error('ERROR: Unexpected error: handler "%s" not found', event['handler_name'])
    sys.exit()

def handler_switch(handler):
    return {
        'update_player_games': update_player_games,
        'update_schedule': update_schedule
    }.get(handler, invalid_handler)

def main(event, context):
    session = init_db_con()
    # session = {}
    try:
        operation = handler_switch(event['handler_name'])
        operation(event, context, session)

        session.commit()
    except Exception as e:
        logger.error(e)
        session.rollback()
        raise
    # finally:
        session.close()


# if __name__ == "__main__":
#     main({
#         'handler_name': 'nope'
#     }, {})
    # main(['4750', '4942'])
    # nba_player = NbaPlayer('4942')

