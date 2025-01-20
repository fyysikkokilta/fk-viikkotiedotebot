import json
import os
from weekly_maker.utils import get_week_number, get_year


class Entry:
    id: str
    category: str
    content: str
    date: tuple[int, int, int]
    title: str
    image: str


class Weekly:
    header: str
    entries: list[Entry]
    footer_image: str


def _save_weekly(content):
    week_number = get_week_number()
    year = get_year()
    os.makedirs(os.path.dirname(f"data/{year}"), exist_ok=True)
    file_name = f"data/{year}/week{week_number:02}.json"
    with open(file_name, "w", encoding="utf8", newline="\n") as f:
        f.write(json.dumps(content))


def _save_weekly_en(content):
    week_number = get_week_number()
    year = get_year()
    os.makedirs(os.path.dirname(f"data/{year}"), exist_ok=True)
    file_name = f"data/{year}/week{week_number:02}-en.json"
    with open(file_name, "w", encoding="utf8", newline="\n") as f:
        f.write(json.dumps(content))


def _load_weekly():
    week_number = get_week_number()
    year = get_year()
    file_name = f"data/{year}/week{week_number:02}.json"
    if not os.path.exists(file_name):
        return {
            "header": "",
            "entries": [],
            "footer_image": "",
        }
    with open(file_name, "r+", encoding="utf8", newline="\n") as f:
        return json.loads(f.read())


def _load_weekly_en():
    week_number = get_week_number()
    year = get_year()
    file_name = f"data/{year}/week{week_number:02}-en.json"
    if not os.path.exists(file_name):
        return {
            "header": "",
            "entries": [],
            "footer_image": "",
        }
    with open(file_name, "r+", encoding="utf8", newline="\n") as f:
        return json.loads(f.read())


def add_entry(entry):
    content = _load_weekly()
    content["entries"].append(entry)
    _save_weekly(content)


def add_entry_en(entry):
    content = _load_weekly_en()
    content["entries"].append(entry)
    _save_weekly_en(content)


def delete_entry(entry_index):
    content = _load_weekly()
    content["entries"].remove(content["entries"][entry_index])
    _save_weekly(content)


def delete_entry_en(entry_index):
    content = _load_weekly_en()
    content["entries"].remove(content["entries"][entry_index])
    _save_weekly_en(content)


def update_header(header):
    content = _load_weekly()
    content["header"] = header
    _save_weekly(content)


def update_header_en(header):
    content = _load_weekly_en()
    content["header"] = header
    _save_weekly_en(content)


def update_footer_image(footer_image):
    content = _load_weekly()
    content["footer_image"] = footer_image
    _save_weekly(content)


def update_footer_image_en(footer_image):
    content = _load_weekly_en()
    content["footer_image"] = footer_image
    _save_weekly_en(content)


def get_entries():
    return _load_weekly()["entries"]


def get_entries_en():
    return _load_weekly_en()["entries"]


def get_weekly():
    return _load_weekly()


def get_weekly_en():
    return _load_weekly_en()
