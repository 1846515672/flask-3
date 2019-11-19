import os

class BaseConfig(object):
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = "hello world"

class DebugConfig(BaseConfig):
    DEBUG = True
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.basename(__file__)))
    SQLALCHEMY_DATABASE_URI = "sqlite:///"+os.path.join(BASE_DIR,"orm.sqlite3")


class RunConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = ""