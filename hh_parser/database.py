import configparser as cfg

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


config = cfg.ConfigParser()
config.read("./hh_parser/hh_config.ini")
engine = create_engine(config["SQLite"]["path"])
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = Session()
Base = declarative_base()
Base.metadata.create_all(bind=engine)



