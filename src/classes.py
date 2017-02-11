from datetime import datetime
import requests
import xlrd

class NbaTeamPage:
    def __init__(self, team_id):
        self.team_id = team_id
        page = requests.get('http://sports.yahoo.com/nba/teams/' + team_id + '/roster/')


def schedule_date(date):
    beforeNYE = ['10', '11', '12']
    month_and_day = date.split('/')
    month = month_and_day[0]
    day = month_and_day[1]
    year = '2016' if month in beforeNYE else '2017'

    if len(day) == 1:
        day = '0' + day

    return datetime.strptime(year + month + day, '%Y%m%d')



class NbaSchedule:
    def __init__(self):
        self.schedule = self.parse_schedule()

    def parse_schedule(sheet_name):
        workbook = xlrd.open_workbook('NBA-2016-17.xls')
        worksheet = workbook.sheet_by_name('vertical')
        num_cols = worksheet.ncols
        schedule = {}

        for col_idx in range(1, num_cols - 1):
            games = []

            for row_idx in range(1, worksheet.nrows):
                if not worksheet.cell(row_idx, col_idx).value == xlrd.empty_cell.value and not worksheet.cell(row_idx, 0).value == 'Date':
                    game = {
                        'date': schedule_date(worksheet.cell(row_idx, 0).value.split('-')[1]),
                        'opp': worksheet.cell(row_idx, col_idx).value
                    }
                    games.append(game)

            schedule[worksheet.cell(0, col_idx).value] = games

        return schedule

    def update_schedule(self):
        




schedule = NbaSchedule()