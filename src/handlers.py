import logging
import sys
from sqlalchemy.orm import sessionmaker
from models import NbaGame, NbaPlayer, create_tables, db_connect
from classes import NbaScheduleSheet

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
        logger.info("SUCCESS: Connection to mysql instance succeeded")

        return session
    except:
        logger.error("ERROR: Unexpected error: Could not connect to mysql instance.")
        sys.exit()


def update_schedule():
    session = init_db_con()




def update_player_games(event, context):
    session = init_db_con()

    try:
        for yahoo_id in event['yahoo_ids']:
            nba_player = NbaPlayerPage(yahoo_id)
            nba_player.update_player_info(session)
            nba_player.update_games(session)

        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        raise
    finally:
        session.close()


# if __name__ == "__main__":
    # main(['4750', '4942'])
    # nba_player = NbaPlayer('4942')

