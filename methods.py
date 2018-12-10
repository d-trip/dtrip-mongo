import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from geopy.geocoders import Nominatim
import requests
from tqdm import tqdm
from steem import Steem
from steem.account import Account
from steem.post import Post


from models import AccountModel, PostModel
from utils import (
    get_check_point,
    set_check_point,
    prepare_post,
    prepare_account,
    get_swm_tag,
    NoSWMTag,
    clean_coordinate
)


steem = Steem()


def parse_location(account):
    location = account['profile'].get('location')

    if AccountModel.objects(
        name=account['name'],
        profile__location=location
       ).first() or location is None:
        # Nothing to update
        return

    geolocator = Nominatim(user_agent="dtrip")
    location = geolocator.geocode(location)
    print(location.latitude, location.longitude)


def update_swm_post(post: str, tag=None):
    post = Post(post).export()
    prepare_post(post)

    tag = get_swm_tag(post['body'])

    if tag:
        lat, lng, desc = get_swm_tag(post['body'])
    else:
        raise NoSWMTag(f'Not contains tag {post["identifier"]}')

    try:
        lat = float(clean_coordinate(lat))
        lng = float(clean_coordinate(lng))

    except Exception as e:
        logging.exception('Parsing coords error')
    else:
        geo = {
          "geometry": {
            "type": "Point",
            "coordinates": [lng, lat]
          },
          "properties": {
            'name': "",
            'desc': desc
          }
        }

        PostModel.objects(identifier=post['identifier']).update(
            **post, geo=geo, upsert=True
        )


def update_post(post: str, swm=False):
    # post = Post(post).export()
    raise NotImplementedError()


def update_account(name):
    account = Account(name).export(load_extras=False)
    prepare_account(account)

    # TODO Parse coordinates
    # parse_location(account)

    AccountModel.objects(name=name).update(**account, upsert=True)


def update_all_accounts():
    pbar = tqdm(
        desc='Update all accounts',
        total=steem.steemd.get_account_count() - AccountModel.objects.count()
    )

    steem.steemd.get_account_count()

    last_user = get_check_point('accounts')

    while True:
        accounts = steem.lookup_accounts(last_user, 1000)

        with ThreadPoolExecutor(max_workers=90) as executor:
            threads = [executor.submit(update_account, a) for a in accounts]

            for thread in as_completed(threads):
                try:
                    thread.result()
                except StopIteration:
                    break
                except Exception as e:
                    logging.exception('Account update')

                pbar.update(1)

        if last_user == accounts[-1]:
            break

        last_user = accounts[-1]
        set_check_point('accounts', last_user)


def update_swm_posts():
    """ Update all SteemitWorldMap posts """
    import xml.etree.ElementTree
    swm_url = ('http://allorigins.me/get?url='
               'https://www.steemitworldmap.com/PHP/search.php')

    raw_xml = requests.get(swm_url).json()['contents']
    e = xml.etree.ElementTree.fromstring(raw_xml)
    # e = xml.etree.ElementTree.parse('swm.xml').getroot()
    posts = [m.get('postLink').split('@')[1] for m in e.findall('marker')]

    pbar = tqdm(
        desc='Update SteemitWorldMap posts',
        total=len(posts)
    )

    with ThreadPoolExecutor(max_workers=80) as executor:
        threads = [executor.submit(update_swm_post, p) for p in posts]

        for thread in as_completed(threads):
            try:
                thread.result()
            except NoSWMTag as e:
                pass
                # print(e)
            except Exception as e:
                logging.exception('Account update')

            pbar.update()
