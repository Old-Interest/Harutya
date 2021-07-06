__author__ = 'Harutya'
__date__ = '2021/07/02'

import re
import threading
import time

import requests
import bs4
from utils import logger

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400",
    "Accept-Language": "zh-CN,zh;q=0.9"
}
item = {}
url = 'http://www.op.gg'
endpoint = '/champion/statistics'


class Info:
    def __init__(self, heroes=None, tiers=None, date=None):
        if heroes is None:
            heroes = {}
        self.date = date
        self.hero = heroes
        self.tiers = tiers


class Tier:
    def __init__(self, position=None, rank=None):
        self.position = position
        self.rank = rank


class Hero:
    def __init__(self, summoner_skills=None, skills=None, equipment=None, rune=None):
        self.summoner_skills = summoner_skills
        self.skills = skills
        self.equipment = equipment
        self.rune = rune


class Skill:
    def __init__(self, name1=None, name2=None, up_rate=None, win_rate=None, skills=None):
        self.name1 = name1
        self.name2 = name2
        self.up_rate = up_rate
        self.win_rate = win_rate
        self.skills = skills


class Equipment:
    def __init__(self, equipment=None, up_rate=None, win_rate=None):
        self.equipment = equipment
        self.up_rate = up_rate
        self.win_rate = win_rate


def op_gg_api():
    info = Info()
    info.tiers = get_tiers()
    info.date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # info.hero = get_all_heroes()
    return info


def get_op_gg():
    response = requests.get(url + endpoint, headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    return soup


def get_hero_url():
    soup = get_op_gg()
    # 获取到英雄列表
    champion_lists = soup.find('div', class_='champion-index__champion-list')
    # 单个英雄div格式匹配
    pattern1 = re.compile('(<div class="champion-index__champion-item .*?</div>)')
    champion_list = re.findall(pattern1, str(champion_lists))
    # 将英雄名和网址作为一个字典
    web_champion = {}
    for champion in champion_list:
        champion_soup = bs4.BeautifulSoup(champion, 'html.parser')
        if champion_soup.div is not None and champion_soup.div.a is not None:
            web_champion[champion_soup.div['data-champion-key']] = url + champion_soup.div.a['href']
    return web_champion


def get_all_heroes():
    heroes = []
    threads = []
    hero_urls = get_hero_url()
    for key in hero_urls.keys():
        threads.append(threading.Thread(target=get_hero, kwargs={"hero_url": hero_urls[key]}))
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
    return heroes


def get_hero(hero_url) -> []:
    logger.Logger().get_log().info(hero_url)
    # 对应英雄查询具体信息
    champion_main, champion_text = getbody(hero_url)
    hero = Hero()
    # 获取召唤师技能
    get_summoner_skills(hero=hero, champion_main=champion_main)
    # 技能加点
    get_skills(hero=hero, champion_main=champion_main)
    # 获取装备信息
    get_equipments(hero=hero, champion_text=champion_text)
    # 获取符文信息
    get_runes(hero=hero, champion_text=champion_text)
    return None


def getbody(body):
    response = requests.get(body, headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    champion_main = soup.find('div', class_="l-champion-statistics-content__main")
    champion_text = champion_main.table

    return champion_main, champion_text


def get_summoner_skills(hero, champion_main):
    # 获取召唤师技能和技能加点
    # 得到第一个tbody也就是包含召唤师技能和加点
    skill_tbody = champion_main.table.tbody

    # 正则匹配召唤师技能名字
    skill_name = []
    pattern2 = re.compile('(<img .*?>)')
    user_skill = re.findall(pattern2, str(skill_tbody))
    for skill in user_skill:
        skill_soup = bs4.BeautifulSoup(skill, 'html.parser')
        skill_name_soup = bs4.BeautifulSoup(skill_soup.img['title'], 'html.parser')
        name = skill_name_soup.b.string
        if name in item.keys():
            name = item[name]
        skill_name.append(name)
    # 正则匹配召唤师技能的登场率和胜率
    skill_rate = []
    pattern3 = re.compile('<strong>(.*?)</strong>')
    rate_ls = re.findall(pattern3, str(skill_tbody))
    for rate in rate_ls:
        skill_rate.append(rate)
    # skill_rate为登场率胜率
    skills = []
    for i in range(0, len(skill_name), 2):
        skill = Skill(name1=skill_name[i], name2=skill_name[i + 1], up_rate=skill_rate[i], win_rate=skill_rate[i + 1])
        skills.append(skill)
    hero.summoner_skills = skills


def get_skills(hero, champion_main):
    skill_tbody = champion_main.table.tbody
    # 获取技能加点
    skill_adds = skill_tbody.find_next_siblings('tbody')
    pattern4 = re.compile(r'<td>([\s,\S]*?)</td>')
    skills = re.findall(pattern4, str(skill_adds))
    skills = ''.join(skills)
    pattern5 = re.compile('(\w*?)')
    skills = re.findall(pattern5, skills)
    skills = ''.join(skills)
    hero.skills = skills


def get_equipments(hero, champion_text):
    equipment_tbody = champion_text.find_next_siblings('table')[0].tbody
    equipment_infos = []
    equipments = []
    pattern6 = re.compile(r'(<tr[\s,\S]*?</tr>)')
    equipment_text = re.findall(pattern6, str(equipment_tbody))
    for text in equipment_text:
        tmp = []
        # 获取装备名
        pattern6 = re.compile('(<li class="champion-stats__list__item tip"[\s,\S]*?</li>)')
        tmp_equipment = re.findall(pattern6, text)
        ls = []
        for i in tmp_equipment:
            temp = bs4.BeautifulSoup(i, 'html.parser')
            temp1 = bs4.BeautifulSoup(temp.li['title'], 'html.parser')
            if temp1.b.string in item.keys():
                ls.append(item[temp1.b.string])
            else:
                ls.append(temp1.b.string)
        tmp.append(ls)
        # 获取登场率和胜率
        pattern7 = re.compile(r'<strong>(.*?)</strong>')
        tmp.append(re.findall(pattern7, text))
        equipment_infos.append(tmp)

        for equip in equipment_infos:
            equipment = Equipment()
            equipment.equipment = equip[0]
            equipment.up_rate = equip[1][0]
            equipment.win_rate = equip[1][1]
            equipments.append(equipment)
        hero.equipment = equipments


def get_runes(hero, champion_text):
    runes_tbody = champion_text.find_next_siblings('div')[0].tbody
    runes_tag = runes_tbody.tr.td.div
    runes_div = runes_tag.div.find_next_siblings('div')
    runes_div.append(runes_tag.div)
    rune_ls = []
    for rune in runes_div:
        tmp = []
        # 匹配符文名
        pattern8 = re.compile(r'<div class="champion-stats-summary-rune__name">(.*?)</div>')
        z = []
        for i in re.findall(pattern8, str(rune.a)):
            s = i.split(' + ')
            if s[0] in item.keys():
                s[0] = item[s[0]]
            if s[1] in item.keys():
                s[1] = item[s[1]]
            z = ' + '.join(s)
        tmp.append(z)
        pattern9 = re.compile(r'<strong>(.*?)</strong>')
        tmp.append(re.findall(pattern9, str(rune.a)))
        pattern10 = re.compile(r'<span>(\d.*?)</span>')
        tmp.append(re.findall(pattern10, str(rune.a)))
        rune_ls.append(tmp)
    # rune_ls格式为[[[符文名],[登场率],[胜率]]]

    rune_name = '\n\n' + '符文'.ljust(35) + '登场率'.ljust(10) + '胜率'.ljust(10) + '\n'
    o = 0
    for rune in rune_ls:
        for j, k in zip(rune[1], rune[2]):
            rune_name = rune[0].ljust(30) + j.ljust(10) + k.ljust(10) + '\n'


def get_tiers():
    tiers = []
    soup = get_op_gg()
    pattern1 = re.compile('"tabItem champion-trend-tier-.*?"')
    positions = re.findall(pattern1, str(soup.contents))
    for position in positions:
        position = str(position).replace('"', '')
        champion_tier = soup.find('tbody', class_=position)
        pattern2 = re.compile('<div class="champion-index-table__name">.*?</div>')
        heroes = re.findall(pattern2, str(champion_tier))
        pattern3 = re.compile('icon-champtier-.1?.png')
        rank = re.findall(pattern3, str(champion_tier))
        tier = Tier()
        for i in range(0, len(heroes), 1):
            tier.rank = [heroes[i], rank[i]]
            tier.position = position.replace("tabItem champion-trend-tier-", "")
            tiers.append(tier)
    return tiers


if __name__ == '__main__':
    op_gg_api()
