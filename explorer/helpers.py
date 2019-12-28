from datetime import datetime

def month_name(month_number):
    month_names = [
                 'January', 'February', 'March', 'April', \
                 'May', 'June', 'July', 'August', 'September', \
                 'October', 'November', 'December',
    ]
    d = {index + 1: month_name for index, month_name in enumerate(month_names)}
    return d[month_number]
    
def truncate_timestamp(datetime_string):
    return datetime_string[:10]
    
def get_leaderboards_options(activities):
    options = []
    for activity in activities:
        option = {}
        option['text'] = '{}, {}'.format(
            activity['name'],
            truncate_timestamp(activity['start_date'])
        )
        option['value'] = activity['id']
        options.append(option)
    return options
    
def timestamp(datestring):
    '''Datestring to datetime to timestamp'''
    dtime = datetime.strptime(datestring, '%Y-%m-%dT%XZ')
    timestamp = datetime.timestamp(dtime)
    return timestamp
    
