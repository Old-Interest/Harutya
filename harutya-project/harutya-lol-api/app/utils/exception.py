__author__ = 'Harutya'
__date__ = '2021/07/09'

from flask import jsonify

from app import app
from utils import harutyaResponse


@app.errorhandler(Exception)
def error_exception(error):
    res = harutyaResponse.error(str(error.original_exception))
    return jsonify(res)


@app.errorhandler(500)
def error_500(error):
    res = harutyaResponse.error(str(error.original_exception))
    return jsonify(res)
