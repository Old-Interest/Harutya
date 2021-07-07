__author__ = 'Harutya'
__date__ = '2021/07/07'

from app.server import opggApi
from flask import Blueprint

servlet = Blueprint('harutya-lol-api', __name__)


@servlet.route('/')
def op_gg_api():
    return opggApi.op_gg_api()
