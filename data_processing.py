import requests
import datetime

weekly_base_url = "https://www.fyysikkokilta.fi/wp-content/uploads/"\
                     "viikkotiedote-data/{year}/{week}.json"
weekly_base_url_en = "https://www.fyysikkokilta.fi/wp-content/uploads/"\
                     "viikkotiedote-data/{year}/{week}-en.json"

weekly_news_url = "https://www.fyysikkokilta.fi/viikkotiedote/"
weekly_news_url_en = "https://www.fyysikkokilta.fi/en/viikkotiedote/"


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


def news_message_fi(news_function):
    def filter_by_date(date):
        event_date = datetime.date(date[2], date[1], date[0])
        today = datetime.date.today()
        return event_date - today < datetime.timedelta(days=8)

    try:
        data = news_function()["_default"].values()
    except KeyError:
        return "Tiedote on tyhjä"

    headers = {"guild_soon": [], "guild": [], "other": []}
    for event in data:
        if (event["category"] == "Killan tapahtumat") & (filter_by_date(event["date"])):
            headers["guild_soon"].append(
                "<a>&#x23F0; {}</a>".format(event["header"])
            )
        elif event["category"] == "Killan tapahtumat":
            headers["guild"].append(
                "<a>&#x2022; {}</a>".format(event["header"])
            )
        else:
            headers["other"].append(
                "<a>&#x2022; {}</a>".format(event["header"])
            )
    guild_events_title = "<b>Killan tapahtumat</b>"
    other_events_title = "\n<b>Muut</b>"
    news_link = "\n<a href=\"{}\">Lue viikkotiedote</a>".format(weekly_news_url)

    message = "\n".join([guild_events_title] + headers["guild_soon"] + headers["guild"] +
                        [other_events_title] + headers["other"] + [news_link])
    return message


def news_message_en(news_function):
    def filter_by_date(date):
        event_date = datetime.date(date[2], date[1], date[0])
        today = datetime.date.today()
        return event_date - today < datetime.timedelta(days=8)

    try:
        data = news_function()["_default"].values()
    except KeyError:
        return "No weekly news"

    headers = {"guild_soon": [], "guild": [], "other": []}
    for event in data:
        if (event["category"] == "Guild's events") & (filter_by_date(event["date"])):
            headers["guild_soon"].append(
                "<a>&#x23F0; {}</a>".format(event["header"])
            )
        elif event["category"] == "Guild's events":
            headers["guild"].append(
                "<a>&#x2022; {}</a>".format(event["header"])
            )
        else:
            headers["other"].append(
                "<a>&#x2022; {}</a>".format(event["header"])
            )
    guild_events_title = "<b>Guild's events</b>"
    other_events_title = "\n<b>Other events</b>"
    news_link = "\n<a href=\"{}\">Read the news</a>".format(weekly_news_url_en)

    message = "\n".join([guild_events_title] + headers["guild_soon"] + headers["guild"] +
                        [other_events_title] + headers["other"] + [news_link])
    return message
