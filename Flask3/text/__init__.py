"""
包实例化文件
项目的实例化
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_restful import Api

bootstrap = Bootstrap()
api = Api()
db = SQLAlchemy()

def cteate_app():
    app = Flask(__name__)
    app.config.from_object("settings.DebugConfig")

    #惰性加载
    bootstrap.init_app(app)
    api.init_app(app)
    db.init_app(app)

    from text.blup import lou_app
    app.register_blueprint(lou_app)
#    app.register_blueprint(lou_app,url_prefix = "/louapp/")
    return app