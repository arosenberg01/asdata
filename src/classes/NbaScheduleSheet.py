from datetime import datetime
import xlrd
from src.models.model import NbaSchedule
from src.utilities import team_mappings

def schedule_date(date):
    beforeNYE = ['10', '11', '12']
    month_and_day = date.split('/')
    month = month_and_day[0]
    day = month_and_day[1]
    year = '2016' if month in beforeNYE else '2017'

    if len(day) == 1:
        day = '0' + day

    return datetime.strptime(year + month + day, '%Y%m%d')

class NbaScheduleSheet:
    def __init__(self):
        self.schedule = self.parse_schedule()

    def parse_schedule(sheet_name):
        workbook = xlrd.open_workbook('NBA-2016-17.xls')
        worksheet = workbook.sheet_by_name('vertical')
        num_cols = worksheet.ncols
        schedule = {}
        teams = {}

        for col_idx in range(1, num_cols - 1):
            games = []

            for row_idx in range(1, worksheet.nrows):
                if not worksheet.cell(row_idx, col_idx).value == xlrd.empty_cell.value and not worksheet.cell(row_idx, 0).value == 'Date':
                    game = {
                        'date': schedule_date(worksheet.cell(row_idx, 0).value.split('-')[1]),
                        'opp': worksheet.cell(row_idx, col_idx).value
                    }
                    games.append(game)

            team = str((worksheet.cell(0, col_idx).value)).lower()

            team_id = team_mappings['abrv_city_to_abrv_full'][team]

            schedule[team_id] = games
            # teams[team_id] = ''

        return schedule

    def update_schedule(self, session):
        for team, schedule in self.schedule.iteritems():
            for game in schedule:
                schedule_game = NbaSchedule(
                    team=team,
                    opp=game.opp,
                    date=game.date
                )

                session.add(schedule_game)

