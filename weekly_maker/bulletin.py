import base64
import os
from functools import partial

from jinja2 import Environment, FileSystemLoader

from weekly_maker.utils import (
    CATEGORIES,
    CATEGORIES_EN,
    get_year,
    grouper,
    category_sort,
    get_week_number,
)
from weekly_maker.crud import get_weekly, get_weekly_en


def create_bulletin():

    week = f"{get_week_number()}"

    year = f"{get_year()}"

    # Define template behaviour.
    env = Environment(
        loader=FileSystemLoader("templates"),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    with open("templates/fk-vaakalogo-fi-70px.png", "rb") as f:
        header_image = "data:image/png;base64, " + base64.b64encode(f.read()).decode()

    communications_officer = os.getenv("COMMUNICATIONS_OFFICER")

    weekly = get_weekly()
    weekly_en = get_weekly_en()

    # Sort first by category to enable grouping.
    entries = weekly["entries"]
    entries_en = weekly_en["entries"]
    entries = sorted(entries, key=partial(category_sort, cats=CATEGORIES))
    entries_en = sorted(entries_en, key=partial(category_sort, cats=CATEGORIES_EN))

    # Group entries.
    pairs = grouper(entries, CATEGORIES)
    pairs_en = grouper(entries_en, CATEGORIES_EN)

    template = env.get_template("cells.html")
    template_en = env.get_template("cells_en.html")
    template_short = env.get_template("cells_short.html")
    variables = {
        "title": "Fyysikkokillan viikkotiedote",
        "header": week + "/" + year + "<br>Kilta tiedottaa<br>Guild News",
        "header_image": header_image,
        "ingress": weekly["header"],
        "ingress_en": weekly_en["header"],
        "footer_image": weekly["footer_image"],
        "footer_image_en": weekly_en["footer_image"],
        "category_events": pairs,
        "category_events_en": pairs_en,
        "communications_officer": communications_officer,
        "telegram_nick": "viestintavastaava",
        "email": "viestintavastaava@fyysikkokilta.fi",
        "week": week,
    }

    tiedote = template.render(variables)
    tiedote_en = template_en.render(variables)
    tiedote_short = template_short.render(variables)

    os.makedirs(os.path.dirname(f"mails/{year}"), exist_ok=True)
    with open(
        f"mails/{year}/kilta-tiedottaa-viikko-{week}.html",
        "w",
        encoding="utf8",
        newline="\n",
    ) as f:
        f.write(tiedote)

    with open(
        f"mails/{year}/kilta-tiedottaa-viikko-{week}-en.html",
        "w",
        encoding="utf8",
        newline="\n",
    ) as f:
        f.write(tiedote_en)

    with open(
        f"mails/{year}/kilta-tiedottaa-viikko-{week}-short.html",
        "w",
        encoding="utf8",
        newline="\n",
    ) as f:
        f.write(tiedote_short)

    return tiedote, tiedote_en, tiedote_short
