"""
控制文件
"""
from text import cteate_app
from text.blup.views import lou_app
from text.models import *
from flask_script import Manager
from flask_script import Command
from flask_migrate import Migrate
from flask_migrate import MigrateCommand

app_hello = cteate_app()
manager = Manager(app_hello)
migrate = Migrate(app_hello, db) #创建数据库管理实例

manager.add_command("db", MigrateCommand)

class Hello(Command):
    def run(self):
        print("hello")

class Runserver(Command):
    def run(self):
        app_hello.run(host="0.0.0.0", port=8000, use_reloader=True)

manager.add_command("hello", Hello)
manager.add_command("runserver", Runserver)


if __name__ == "__main__":
    # db.create_all(lou_app)
    manager.run()