import multiprocessing as ml
from hh_parser.parser_app import main as pr

from hh_parser import create_app

from hh_parser.database import db_session, Base, engine

# Создать приложение Flask
app = create_app()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.close()


def create_db():
    Base.metadata.drop_all(engine)
    # Создание новых таблиц
    Base.metadata.create_all(engine)
    db_session.close()

if __name__ == "__main__":


    # Зпустить парсер
    par_service = ml.Process(name="HH API Parse", target=pr.main)
    par_service.start()

    # Запустить Flask приложение
    app.run()
