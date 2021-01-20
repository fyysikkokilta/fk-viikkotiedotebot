import requests
import datetime

weekly_base_url = "https://www.fyysikkokilta.fi/wp-content/uploads/"\
                     "viikkotiedote-data/{year}/{week}.json"
weekly_base_url_en = "https://www.fyysikkokilta.fi/wp-content/uploads/"\
                     "viikkotiedote-data/{year}/{week}-en.json"


def get_weekly_data(year, week_number, base_url=weekly_base_url):
    week_string = "week{:02}".format(week_number)
    url = base_url.format(year=year, week=week_string)
    return requests.get(url).json()


def current_news(base_url=weekly_base_url):
    today = datetime.date.today()
    year, week_number = today.isocalendar()[0:2]
    return get_weekly_data(year, week_number, base_url)


def current_news_en():
    return current_news(weekly_base_url_en)


def next_week_news(base_url=weekly_base_url):
    today = datetime.date.today()
    next_week = today + datetime.timedelta(days=7)
    year, week_number = next_week.isocalendar()[0:2]
    return get_weekly_data(year, week_number, base_url)


def next_week_news_en():
    return next_week_news(weekly_base_url_en)
