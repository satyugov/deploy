from flask import Flask

SECRET_KEY = b'\x143#\x1eV;\xc9\xa0\xecr\r\xd4/{b\n'


app = Flask(__name__)
app.config.from_object(__name__)


def create_app():
    return app
