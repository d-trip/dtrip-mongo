X_DOMAINS = '*'

DOMAIN = {
    'accounts': {
        'schema': {
            'name': {'type': 'string'},
            'profile': {'type': 'dict'},
            'post_count': {'type': 'integer'},
            'last_post': {'type': 'datetime'},
            'reputation': {'type': 'integer'},
        },

        'datasource': {'source': 'account_object'},
        'resource_methods': ['GET']
    },

    'posts': {
        'schema': {
            'title': {'type': 'string'},
            'author': {'type': 'string'},
            'permlink': {'type': 'string'},
            'created': {'type': 'datetime'},
            'geo': {'type': 'dict'},
        },

        'datasource': {'source': 'post_object'},
        'resource_methods': ['GET']
    }
}


PAGINATION_LIMIT = 1000


MONGO_QUERY_BLACKLIST = ['$where', '$regex']

# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET']

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

try:
    from settings_local import *
except:
    pass
