import configparser as cfg
import time
import sys
from .process_request import read_requests, process_request
from .database import db_session



def main():
    # Читаем конфигурационные параметры
    config = cfg.ConfigParser()
    config.read("./hh_parser/hh_config.ini")
    sqlite_dbb = config["SQLite"]["path"]
    file_folder = config["Json"]["path"]

    i_cycle = 0
    while True:
        # Читаем записи со статусом 0 из БД
        rows = read_requests(db_session)
        if rows:
            # Если записи найдены, то начинаем обработку.
            # Перебираем запросы из базы данных и запускаем обработку каждого из них.
            # Также не забываем добавить извлечение настроек из ini-файла.
            for row_request in rows:
                print(f"\nОбработка запроса: "
                      f"{row_request.region}"
                      f"{row_request.text_request} начата.")
                process_request(db_session, file_folder, row_request)
                print(f"\nОбработка запроса: "
                      f"{row_request.region}"
                      f"{row_request.text_request} завершена.")
        else:
            # Переходим в режи ожидания
            time.sleep(5)
            sys.stdout.write("\r")
            sys.stdout.write(f"Новых запросов не найдено, Цикл {i_cycle}")
        i_cycle += 1
