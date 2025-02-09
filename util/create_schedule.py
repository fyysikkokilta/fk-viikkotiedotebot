import json


def create(filename: str):
    data = {
        "messages": [
            {"chat_id": -73262859263, "language": "fi"},
            {"chat_id": -89375372901, "language": "en"},
        ]
    }
    with open(filename, "w", encoding="utf8", newline="\n") as outfile:
        json.dump(data, outfile)


if __name__ == "__main__":
    create("schedule.txt")
