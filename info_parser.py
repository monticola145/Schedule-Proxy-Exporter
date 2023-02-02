import logging
import os
from datetime import datetime, timedelta
from os.path import dirname, join
from time import sleep

from dotenv import load_dotenv

from misc import parser
from OpencastAPI.opencast_api import OpencastAPI
from OpencastAPI.series_creator import series_poster

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
logging.basicConfig(
    level=logging.INFO,
    encoding="UTF-8",
    filename="py_log.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
)


def time_shifter(begin_time=None, end_time=None):
    if begin_time is not None:
        begin_time = "T".join(
            str(
                datetime.strptime(
                    " ".join(begin_time.split("Z")[0].split("T")), "%Y-%m-%d %H:%M:%S"
                )
                + timedelta(seconds=int(os.getenv("EVENT_BEGIN_OFFSET_SECONDS")))
            ).split(" ")
        )
        return begin_time
    if end_time is not None:
        end_time = "T".join(
            str(
                datetime.strptime(
                    " ".join(end_time.split("Z")[0].split("T")), "%Y-%m-%d %H:%M:%S"
                )
                + timedelta(seconds=int(os.getenv("EVENT_END_OFFSET_SECONDS")))
            ).split(" ")
        )
        return end_time


def time_formatter(time=None):
    year, month, day = time.split("T")[0].split("-")
    return f"{day}.{month}.{year}"


def info_parser():
    try:
        info = parser()
        logging.info("Данные получены из БД")
        for target_lesson in info:
            title = (
                "TEST "
                + target_lesson[1]
                + " - "
                + target_lesson[2]
                + " - "
                + time_formatter(target_lesson[0])
            )
            OpencastAPI().post_event(
                location_id=target_lesson[3],
                title=title,
                subject=target_lesson[2],
                rightsHolder=None,
                loicense=None,
                isPartOf=series_poster(
                    title=target_lesson[1], subject=target_lesson[2]
                ),
                creator=target_lesson[6],
                contributor=None,
                source=None,
                schedule_event_id=target_lesson[4],
                start_time=time_shifter(begin_time=target_lesson[0]),
                end_time=time_shifter(end_time=target_lesson[5]),
                created=None,
            )
            logging.info("Итерация завершена")
            sleep(5)

    except Exception as error:
        logging.critical(f"Программа поймала исключение: {error}", exc_info=True)
        pass
