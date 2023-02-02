from os.path import dirname, join

import schedule
from dotenv import load_dotenv

from info_parser import info_parser

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


def upload():
    info_parser()
    print("Скрипт завершил итерацию. Режим гибернации.")


def main():
    print("Ожидание начала работы")
    schedule.every().day.at("09:25").do(upload)
    schedule.every().day.at("11:05").do(upload)
    schedule.every().day.at("12:45").do(upload)
    schedule.every().day.at("12:55").do(upload)
    schedule.every().day.at("14:35").do(upload)
    schedule.every().day.at("16:15").do(upload)
    schedule.every().day.at("17:55").do(upload)
    schedule.every().day.at("18:05").do(upload)
    schedule.every().day.at("20:00").do(upload)
    schedule.every().day.at("23:04").do(upload)

    while True:
        schedule.run_pending()


if __name__ == "__main__":
    main()
