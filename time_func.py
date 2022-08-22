from datetime import datetime, timedelta
from sys import exit
import time


def add_spec_text(day, text):           # добавить "Ровно N лет назад..."
    current_year = datetime.now().year
    date = day.replace("_", " ")

    try:
        year = str(current_year - int(text[:4]))
    except ValueError:
        exit('Какая-то фигня с текстом на вики. Ничего не подеелаешь. Перезапускаем.')

    if year[-1] == '1':
        year_word = 'год'
    elif year[-1] == '2' or year[-1] == '3' or year[-1] == '4':
        year_word = 'года'
    else:
        year_word = 'лет'

    return 'Ровно {0} {1} назад, {2} {3} г. — {4}'.format(year, year_word, date, text[:4], text[7:])


def get_days_from_tomorrow_plus(next_days_lst_len, month, add_days=0):
    """
    Получить дни в текстовом и unix формате, начиная с (завтра + add_days)
    """
    days = [datetime.today().date() + timedelta(days=add_days)]
    days_unix = [int(time.mktime((datetime.today().date() + timedelta(days=add_days)).timetuple()))]

    for i in range(next_days_lst_len):
        days.append(days[0] + timedelta(days=i + 1))
        days_unix.append(int(time.mktime(days[-1].timetuple())))

    for i in range(len(days)):
        d, m = days[i].strftime('%d_%m').split('_')
        if d.startswith('0'):
            d = d[1:]
        days[i] = f'{d}_{month[int(m) - 1]}'

    return days[1:], days_unix[1:]


def get_delay_lst(hour_interval: int):      # получить delay для отложенных постов
    max_posts = int(24 / hour_interval)     # кол-во постов в день

    delay = []
    for i in range(max_posts):
        delay.append(i * hour_interval * 3600)

    return delay
