from flask import Blueprint

lou_app = Blueprint("lou_app", __name__)

from text.blup import views
