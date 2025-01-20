from datetime import date, datetime, timedelta
from itertools import groupby
from functools import partial


CATEGORIES = ["Opinnot", "Killan tapahtumat", "Muut tapahtumat", "Yleistä"]
CATEGORIES_EN = ["Studies", "Guild's events", "Other events", "General"]


def get_week_number():
    return int((date.today() + timedelta(days=6)).strftime("%V"))


def get_year():
    return datetime.now().year


# Functions for grouping and sorting database entries.
def category_sort(x, cats):
    """Return index of database entry's category from a given list."""
    return cats.index(x["category"])


def date_sort(x):
    """Return date of database-entry."""
    return date(x["date"][2], x["date"][1], x["date"][0])


def in_current_week(x):
    """Test whether entry's date is on current week."""
    return (
        int(
            (
                date(x["date"][2], x["date"][1], x["date"][0]) - timedelta(days=1)
            ).strftime("%U")
        )
        + 1
        == get_week_number()
    )


def grouper(entries, cats):
    """Return tuple, which consists of string and another tuple, which consist of two lists.
    First entries are grouped by category and sorted by date. Then they are sorted even
    further to events that happen this week and events that happen later in the future.
    """
    category_and_events = []
    for k, g in groupby(entries, key=partial(category_sort, cats=cats)):
        events_sorted = sorted(list(g), key=date_sort)

        this_week = [e for e in events_sorted if in_current_week(e)]
        following_week = [e for e in events_sorted if not in_current_week(e)]

        category_and_events.append((cats[k], (this_week, following_week)))
    return category_and_events
