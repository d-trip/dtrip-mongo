import re
from datetime import datetime

from models import db

from steem.blockchain import Blockchain


def prepare_post(post):
    post.pop('id')
    post['tags'] = list(post['tags'])


def prepare_account(account):
    account.pop('id')

    time_convert = [
        'created',
        'last_post',
        'last_root_post',
        'last_account_recovery',
        'last_account_update',
        'last_owner_update',
        'last_vote_time'
    ]

    for k in time_convert:
        account[k] = datetime.strptime(account[k], "%Y-%m-%dT%H:%M:%S")


def get_current_block_num():
    return Blockchain().get_current_block_num()


def get_check_point(check_point):
    return db.state.find_one().get(check_point)


def set_check_point(check_point, value):
    return db.state.update_one({}, {"$set": {check_point: value}})


def get_swm_tag(body):
    match = re.search(
        # '!?!steemitworldmap([-\s.,\d]*?)lat([-\s.,\d]*?)long(.*?(?=d3scr))?',
        '!steemitworldmap(.*?)lat(.*?)long(.*?(?=d3scr))?',
        body, re.M | re.I | re.S
    )

    if match:
        return [g.strip() if g else '' for g in match.groups()]

    return None


class NoSWMTag(Exception):
    pass


def clean_coordinate(c):
    c = re.sub(r'<[^>]*?>', '', c)
    c = re.sub(',\d+', '', c)
    c = re.sub('[^\d\.\-\+]', '', c)

    if c.count('.') > 1:
        c = '.'.join(c.split('.')[:2])

    if c.count('-') > 1 and re.findall('-[\d.]+', c):
        c = re.findall('-[\d.]+', c)[0]

    return c
