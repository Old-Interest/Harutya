__author__ = 'Harutya'
__date__ = '2021/07/02'

from flask import Flask
from app import routes

app = Flask(__name__)

app.register_blueprint(routes.servlet, url_prefix='/harutya-lol-api')



