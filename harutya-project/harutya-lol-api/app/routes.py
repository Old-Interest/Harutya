__author__ = 'Harutya'
__date__ = '2021/07/07'

from app.server import opggApi
from flask import Blueprint
from utils import harutyaResponse

servlet = Blueprint('harutya-lol-api', __name__)


@servlet.route('/tiers')
def tiers():
    return harutyaResponse.success(opggApi.get_tiers())


@servlet.route('/heroes')
def heroes():
    return harutyaResponse.success(opggApi.get_hero_url())


@servlet.route('/hero/<string:hero_name>')
def hero(hero_name):
    return harutyaResponse.success(opggApi.get_hero(hero_name))
