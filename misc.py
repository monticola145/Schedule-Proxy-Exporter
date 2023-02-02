import json
import os
from datetime import datetime
from os.path import dirname, join

import requests
from alive_progress import alive_bar
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


def parser():
    url = os.getenv("SCHEDULE_API_URL")
    bearer = os.getenv("AUTHORIZATION")
    b = 0
    d = str(datetime.now())
    c = ()

    with open("OpencastAPI/mapping.json", "r") as openfile:
        mapping = json.load(openfile)
        auds = list([aud for aud in [aud.keys() for aud in mapping][0]])

    with alive_bar(100, title="Выгрузка данных из БД", bar="blocks") as bar:
        while b < 100:
            b += 1
            a = requests.get(
                f"{url}/lessons?page={b}&per_page=100",
                headers={"Authorization": f"Bearer {bearer}"},
            ).json()
            if len(list(filter(lambda x: x["begins_at"][:10] == d[:10], a))) > 0:
                c = c + (tuple(filter(lambda x: x["begins_at"][:10] == d[:10], a)))
                bar()
            else:
                bar()
    h = []
    for event in c:
        if event["auditorium_title"] in auds:
            try:
                event = (
                    event["begins_at"],
                    event["course_name"],
                    event["group_name"],
                    event["auditorium_title"],
                    event["_id"],
                    event["ends_at"],
                    event["lecturers"][0]["full_name"],
                )
                h.append(event)
            except TypeError:
                event = (
                    event["begins_at"],
                    event["course_name"],
                    event["group_name"],
                    event["auditorium_title"],
                    event["_id"],
                    event["ends_at"],
                )

    h = sorted(h, key=lambda tup: (tup[0], tup[1]))

    return h
