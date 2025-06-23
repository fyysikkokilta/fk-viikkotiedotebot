import datetime

weekly_base_url = "mails/{year}/kilta-tiedottaa-viikko-{week:02}-short.html"
weekly_base_url_en = "mails/{year}/kilta-tiedottaa-viikko-{week:02}-short-en.html"


def get_weekly_data(year, week, base_url=weekly_base_url):
    url = base_url.format(year=year, week=week)
    try:
        with open(url, "r+", encoding="utf8", newline="\n") as f:
            data = f.read()
    except FileNotFoundError:
        data = ""
    return data


def current_news(base_url=weekly_base_url):
    today = datetime.date.today()
    year, week = today.isocalendar()[0:2]
    return get_weekly_data(year, week, base_url)


def current_news_en():
    return current_news(weekly_base_url_en)
