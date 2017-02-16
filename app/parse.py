from datetime import datetime, timedelta
from . import app

class Days():
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', \
    'saturday', 'sunday']
    next_days = ['next monday', 'next tuesday', 'next wednesday', \
    'next thursday', 'next friday', 'next saturday', 'next sunday']
    terms = ['today', 'tomorrow', 'next week', 'next month', '']


def parse_checkin(checkin_text):
    if checkin_text == '':
        next_checkin = datetime.utcnow().date() + timedelta(days=30)
        return next_checkin
    elif checkin_text == 'today':
        next_checkin = datetime.utcnow().date()
        return next_checkin
    elif checkin_text == 'tomorrow':
        next_checkin = datetime.utcnow().date() + timedelta(days=1)
        return next_checkin
    elif checkin_text == 'next week':
        next_checkin = datetime.utcnow().date() + timedelta(days=7)
        return next_checkin
    elif checkin_text == 'next month':
        pass
        # Get current date
        # Increment month by one (and year by one if need be)
        # Check if the resulting date is Saturday or Sunday
        # If so, increment date such that the weekday is Monday
    elif checkin_text in Days.days:
        return parse_day_of_week(checkin_text)
    elif checkin_text in Days.next_days:
        return parse_next_day_of_week(checkin_text)
    else:
        try:
            datetime.strptime(checkin_text, '%Y-%m-%d')
        except ValueError:
            flash('Invalid input')
            return redirect(url_for('add_contact'))
        next_checkin = checkin_text
        return next_checkin


def parse_day_of_week(day):
    target = Days.days.index(day)
    date = datetime.utcnow().date()
    today = datetime.weekday(date)
    delta = target - today
    if delta <= 0:
        delta += 7
    next_checkin = datetime.utcnow().date() + timedelta(days=delta)
    return next_checkin


def parse_next_day_of_week(day):
    target = Days.next_days.index(day)
    today = datetime.weekday(datetime.utcnow().date())
    delta = target - today
    if delta <= 0:
        delta += 7
    delta +=7
    next_checkin = datetime.utcnow().date() + timedelta(days=delta)
    return next_checkin


@app.template_filter('friendly_dates')
def friendly_dates(date):
    if date == None:
        return date
    else:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        if date < datetime.utcnow().date():
            date = date
        elif date == datetime.utcnow().date():
            date = 'today'
        elif date == datetime.utcnow().date() + timedelta(days=1):
            date = 'tomorrow'
        elif date <= datetime.utcnow().date() + timedelta(days=6):
            date_index = datetime.weekday(date)
            date = Days.days[date_index]
        elif date == datetime.utcnow().date() + timedelta(days=7):
            date_index = datetime.weekday(date)
            date = 'next %s' % (Days.days[date_index])
        elif date > datetime.utcnow().date() + timedelta(days=7):
            date = datetime.strftime(date, '%Y-%m-%d')
        return date