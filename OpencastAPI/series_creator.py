import codecs
import json
import os
# import pprint
# import traceback
from os.path import dirname, join

import requests
from dotenv import load_dotenv

from .opencast_api import OpencastAPI

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


url = OpencastAPI().api_url


def series_poster(title=None, subject=None):
    title = f"{title} - {subject}"
    response = requests.get(
        f"{url}/series/?limit=1000&offset=1210",
        auth=(os.getenv("OPENCAST_API_USER"), os.getenv("OPENCAST_API_PASSWORD")),
    )
    if len(list(filter(lambda x: x["title"] == title, response.json()))) > 0:
        return list(filter(lambda x: x["title"] == title, response.json()))[0][
            "identifier"
        ]
    else:
        with open("opencastAPI/acl.json") as openfile:
            acl = json.dumps(json.load(openfile), ensure_ascii=False)

        with codecs.open(
            "OpencastAPI/series_metadata.json", "r", encoding="utf-8"
        ) as openfile:
            metadata = json.load(openfile)
            metadata[0]["fields"][0]["value"] = title
            metadata[0]["fields"][1]["value"] = [subject]

            metadata = json.dumps(metadata, ensure_ascii=False)

            body = {
                "metadata": (None, metadata),
                "acl": (None, acl),
            }
            headers = {
                "content-disposition": "form-data",
                "cache-control": "no-cache",
                "Connection": "close",
            }

            response = requests.post(
                f"{url}/series",
                files=body,
                headers=headers,
                auth=(
                    os.getenv("OPENCAST_API_USER"),
                    os.getenv("OPENCAST_API_PASSWORD"),
                ),
            )

            identifier = response.json()["identifier"]
            response = requests.get(
                f"{url}/series/{identifier}",
                auth=(
                    os.getenv("OPENCAST_API_USER"),
                    os.getenv("OPENCAST_API_PASSWORD"),
                ),
            )

            return identifier
