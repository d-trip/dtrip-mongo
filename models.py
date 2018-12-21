import os
from mongoengine import DynamicDocument
from pymongo import MongoClient
from mongoengine.fields import (
    StringField, DictField, DateTimeField
)

from mongoengine import connect


URI = 'mongodb://'

name = os.getenv('DB_NAME', 'DTripData')
host = os.getenv('MONGO_HOST', 'localhost')
username = os.getenv('MONGO_USER')
password = os.getenv('MONGO_PASSWORD')
port = int(os.getenv('MONGO_PORT', 27017))

if username and password:
    URI += f'{username}:{password}@'

URI += f'{host}:{port}/{name}?authSource=admin'


mongo = connect(
    name,
    host=URI,

    # FIXME MongoEngine bug, authentication not working
    # username=os.getenv('MONGO_USER'),
    # password=os.getenv('MONGO_PASSWORD'),

    # host=os.getenv('MONGO_HOST', 'localhost'),
    # port=int(os.getenv('MONGO_PORT', 27017))
)

db = mongo[os.getenv('DB_NAME', 'DTripData')]


class PostModel(DynamicDocument):
    author = StringField()
    permlink = StringField()
    created = DateTimeField()

    meta = {
        'collection': 'post_object',
        'indexes': [
            'author',
            'permlink',
            'created',

            {'fields': ['$title', '$body'],
             'default_language': 'english',
             'weights': {'title': 10, 'body': 2}}
        ],

        'auto_create_index': True,
        'index_background': True
    }


class AccountModel(DynamicDocument):
    name = StringField()
    profile = DictField()

    created = DateTimeField()
    last_post = DateTimeField()
    last_root_post = DateTimeField()
    last_account_recovery = DateTimeField()
    last_account_update = DateTimeField()
    last_owner_update = DateTimeField()
    last_vote_time = DateTimeField()

    meta = {
        'collection': 'account_object',
        'indexes': [
            'sp',
            'name',
            'created',
            'last_post',
            'post_count',
            'reputation',
            'reset_account',
            'profile.wants_meet_up',
            'profile.accepting_guests',

            # For multiple sort
            ['sp',
             'last_post',
             'profile.wants_meet_up',
             'profile.accepting_guests'],

            {'fields': ['$profile.about', '$profile.location', '$name'],
             'default_language': 'english',
             'weights': {'profile.about': 10,
                         'profile.location': 10,
                         'name': 10}}
        ],

        'auto_create_index': True,
        'index_background': True
    }


if not db.state.find_one():
    db.state.insert_one({'last_block': 1, 'accounts': 'a-0'})
