from datetime import datetime

def game_date(date):
    beforeNYE = ['Oct', 'Nov', 'Dec']
    month_and_day = date.split(' ')
    month = month_and_day[0]
    day = month_and_day[1]
    year = '2016' if month in beforeNYE else '2017'

    if len(day) == 1:
        day = '0' + day

    return datetime.strptime(year + month + day, '%Y%b%d')

def sec_played(time):
    minutes_and_sec = time.split(':')

    return int(minutes_and_sec[0]) * 60 + int(minutes_and_sec[1])

team_mappings = {
    'abrv_city_to_abrv_full': {
        'bos': 'bos',
        'bkn': 'bro',
        'cle': 'cle',
        'ny':  'nyk',
        'phi': 'phi',
        'tor': 'tor',
        'chi': 'chi',
        'det': 'det',
        'ind': 'ind',
        'mil': 'mil',
        'atl': 'atl',
        'cha': 'cha',
        'mia': 'mia',
        'orl': 'orl',
        'was': 'was',
        'gsw': 'gsw',
        'lac': 'lac',
        'lal': 'lal',
        'pho': 'pho',
        'dal': 'dal',
        'hou': 'hou',
        'mem': 'mem',
        'no':  'nor',
        'sa':  'sas',
        'den': 'den',
        'min': 'min',
        'okc': 'okc',
        'por': 'por',
        'sac': 'sac',
        'uth': 'uth'
    },
    'city_full_to_abrv': {
         'Boston': 'bos',
         'Brooklyn': 'bro',
         'New York': 'nyk',
         'Philadelphia': 'phi',
         'Toronto': 'tor',
         'Chicago': 'chi',
         'Detroit': 'det',
         'Indianapolis': 'ind',
         'Milwaukee': 'mil',
         'Atlanta': 'atl',
         'Charlotte': 'cha',
         'Miami': 'mia',
         'Orlando': 'orl',
         'Washington': 'was',
         'Golden State': 'gsw',
         'LA Clippers': 'lac',
         'LA Lakers': 'lal',
         'Phoenix': 'pho',
         'Dallas': 'dal',
         'Houston': 'hou',
         'Memphis': 'mem',
         'New Orleans': 'nor',
         'San Antonio': 'sas',
         'Denver': 'den',
         'Minnesota': 'min',
         'Oklahoma City': 'okc',
         'Portland': 'por',
         'Utah':' uth'
    }
}