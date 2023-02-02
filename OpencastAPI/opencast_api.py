import codecs
import json
import logging
import os
# import pprint
# import traceback
from datetime import datetime, timedelta
from os.path import dirname, join

import pytz
import requests
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
logging.basicConfig(
    level=logging.INFO,
    encoding="UTF-8",
    filename="py_log.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
)


class OpencastAPI:
    def __init__(self):
        self.api_url = os.getenv("OPENCAST_API_URL")

    def time_transformer(self, time=None):
        try:
            if "Z" not in time:
                return (
                    "T".join(
                        (
                            str(
                                datetime.strptime(
                                    time.split("+")[0], "%Y-%m-%d"
                                ).astimezone(pytz.UTC)
                            )[:19]
                        ).split(" ")
                    )
                    + ".000Z"
                )
            else:
                return (
                    "T".join(
                        str(
                            datetime.strptime(
                                " ".join(time.split("Z")[0].split("T")),
                                "%Y-%m-%d %H:%M:%S",
                            )
                            + timedelta(hours=0)
                        ).split(" ")
                    )
                    + ".000Z"
                )
                #  создатели опенкаста обожают туда-сюда дёргать время, поэтому редактируйте timedelta(hours=n) в зависимости от смещения от целевого времени при постинге
        except Exception:
            return (
                "T".join(
                    (
                        str(
                            datetime.strptime(
                                time.split("+")[0], "%Y-%m-%dT%H:%M:%S"
                            ).astimezone(pytz.UTC)
                        )[:19]
                    ).split(" ")
                )
                + ".000Z"
            )
            pass

    def time_checker(self, time=None):
        try:
            if "Z" not in time:
                return (
                    "T".join(
                        (
                            str(
                                datetime.strptime(
                                    time.split("+")[0], "%Y-%m-%d"
                                ).astimezone(pytz.UTC)
                            )[:19]
                        ).split(" ")
                    )
                    + "Z"
                )
            else:
                return (
                    "T".join(
                        str(
                            datetime.strptime(
                                " ".join(time.split("Z")[0].split("T")),
                                "%Y-%m-%d %H:%M:%S",
                            )
                            + timedelta(hours=0)
                        ).split(" ")
                    )
                    + "Z"
                )
                #  создатели опенкаста обожают туда-сюда дёргать время, поэтому редактируйте timedelta(hours=n) в зависимости от смещения от целевого времени при постинге
        except Exception:
            return (
                "T".join(
                    (
                        str(
                            datetime.strptime(
                                time.split("+")[0], "%Y-%m-%dT%H:%M:%S"
                            ).astimezone(pytz.UTC)
                        )[:19]
                    ).split(" ")
                )
                + "Z"
            )
            pass

    def post_event(
        self,
        title=None,
        subject=None,
        rightsHolder=None,
        loicense=None,
        isPartOf=None,
        creator=None,
        contributor=None,
        source=None,
        schedule_event_id=None,
        location_id=None,
        start_time=None,
        end_time=None,
        created=None,
    ):
        """Принимает метаданные eventа из schedule_proxy и
        использует их при создании eventа в Opencast, затем
        возвращает id созданного eventа
        """
        try:
            response_check = requests.get(
                f"{self.api_url}/events/",
                auth=(
                    os.getenv("OPENCAST_API_USER"),
                    os.getenv("OPENCAST_API_PASSWORD"),
                ),
            )

            with open("OpencastAPI/mapping.json", "r") as openfile:
                location = json.load(openfile)
                location = location[0][location_id]

            with open("OpencastAPI/acl.json") as openfile:
                acl = json.dumps(json.load(openfile), ensure_ascii=False)

            with codecs.open(
                "OpencastAPI/metadata.json", "r", encoding="utf-8"
            ) as openfile:
                metadata = json.load(openfile)
                metadata[0]["fields"][0]["value"] = title
                metadata[0]["fields"][1]["value"] = [subject]
                metadata[0]["fields"][2][
                    "value"
                ] = f"Событие успешно импортировано из Schedule-proxy. ID: {schedule_event_id}"
                metadata[0]["fields"][6]["value"] = isPartOf
                metadata[0]["fields"][7]["value"] = [creator]
                metadata[0]["fields"][9]["value"] = self.time_transformer(start_time)
                metadata[0]["fields"][13]["value"] = source

                metadata = json.dumps(metadata, ensure_ascii=False)

            with open("OpencastAPI/scheduling.json", "r") as openfile:
                scheduling = json.load(openfile)

                scheduling["start"] = self.time_transformer(start_time)
                scheduling["end"] = self.time_transformer(end_time)
                scheduling["agent_id"] = location

                scheduling = json.dumps(scheduling, ensure_ascii=False)

            with open("OpencastAPI/processing.json", "r") as openfile:
                processing = json.load(openfile)

                processing["workflow"] = os.getenv("OPENCAST_WORKFLOW_ID")

                processing = json.dumps(processing, ensure_ascii=False)

            body = {
                "metadata": (None, metadata),
                "acl": (None, acl),
                "processing": (None, processing),
                "scheduling": (None, scheduling),
            }
            headers = {
                "content-disposition": "form-data",
                "cache-control": "no-cache",
                "Connection": "close",
            }

            response = requests.post(
                f"{self.api_url}/events",
                files=body,
                headers=headers,
                auth=(
                    os.getenv("OPENCAST_API_USER"),
                    os.getenv("OPENCAST_API_PASSWORD"),
                ),
            )

            if (
                response.status_code == 409
                and len(
                    list(
                        filter(
                            lambda x: x["start"] == self.time_checker(start_time),
                            response_check.json(),
                        )
                    )
                )
                != 0
            ):
                logging.warning("Событие уже экспортировано в Опенкаст")
            elif (
                response.status_code == 409
                and len(
                    list(
                        filter(
                            lambda x: x["start"] == self.time_checker(start_time),
                            response_check.json(),
                        )
                    )
                )
                == 0
            ):
                if (
                    len(
                        list(
                            filter(lambda x: x["title"] == title, response_check.json())
                        )
                    )
                    == 0
                ):
                    logging.warning("Данное время занято иным событием")

                elif (
                    len(
                        list(
                            filter(lambda x: x["title"] == title, response_check.json())
                        )
                    )
                    > 0
                    and len(
                        list(
                            filter(
                                lambda x: x["start"] == self.time_checker(start_time),
                                response_check.json(),
                            )
                        )
                    )
                    == 0
                ):
                    logging.warning("Замечен дубликат, удаляем...")
                    deleting_event_id = list(
                        filter(lambda x: x["title"] == title, response_check.json())
                    )[0]["identifier"]
                    response = requests.delete(
                        f"{self.api_url}/events/{deleting_event_id}",
                        auth=(
                            os.getenv("OPENCAST_API_USER"),
                            os.getenv("OPENCAST_API_PASSWORD"),
                        ),
                    )
                    logging.info("Дубликат удалён")
                    response = requests.post(
                        f"{self.api_url}/events",
                        files=body,
                        headers=headers,
                        auth=(
                            os.getenv("OPENCAST_API_USER"),
                            os.getenv("OPENCAST_API_PASSWORD"),
                        ),
                    )
                    logging.info("Событие успешно экспортировано в Опенкаст")

            else:
                if response.status_code == 201:
                    logging.info("Событие успешно экспортировано в Опенкаст")
                else:
                    msg = response.status_code
                    logging.error(
                        f"Не удалось экспортировать событие в Опенкаст: {msg}"
                    )

        except Exception as error:
            logging.critical(f"Программа поймала исключение: {error}")
            pass
