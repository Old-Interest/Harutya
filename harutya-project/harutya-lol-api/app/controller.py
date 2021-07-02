__author__ = 'Harutya'
__date__ = '2021/07/02'

from flask import Flask

app = Flask(__name__)


@app.route("/run")
def run():
    return
