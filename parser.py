from steem import Steem
from steem.blockchain import Blockchain
from steem.instance import set_shared_steemd_instance

from methods import update_account, update_swm_post
from utils import (
    set_check_point,
    get_check_point,
    get_current_block_num,
    get_swm_tag
)


steem = Steem(['https://api.steemit.com/',
               'https://appbasetest.timcliff.com/',
               'https://steemd.minnowsupportproject.org/',
               'https://steemd.privex.io/',
               'https://anyx.io',
               'https://api.steem.house/'], maxsize=100)

set_shared_steemd_instance(steem)

blockchain = Blockchain()


def stream(BLOCK_NUM=None):
    if BLOCK_NUM is None:
        BLOCK_NUM = get_check_point('last_block') or get_current_block_num()

    print(f'START STREAMING FROM BLOCK: {BLOCK_NUM}')
    for op in blockchain.stream(start_block=BLOCK_NUM):
        op_type = op['type']

        def construct_identifier():
            return '@%s/%s' % (
                op.get('author', op.get('comment_author')),
                op.get('permlink', op.get('comment_permlink')),
            )

        if op_type in ['account_create',
                       'create_claimed_account',
                       'account_create_with_delegation']:
            update_account(op['creator'])
            update_account(op['new_account_name'])

        elif op_type in ['author_reward', 'comment']:
            update_account(op['author'])

            if op_type == 'comment':
                swm_tag = get_swm_tag(op['body'])

                if swm_tag:
                    update_swm_post(construct_identifier(), swm_tag)

        elif op_type == 'account_update':
            update_account(op['account'])

        # Update state
        if op['block_num'] != BLOCK_NUM:
            set_check_point('last_block', op['block_num'])
            BLOCK_NUM = op['block_num']
