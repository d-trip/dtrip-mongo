import argparse
from contextlib import suppress

from parser import stream
from methods import update_all_accounts, update_swm_posts
from utils import set_check_point, get_current_block_num

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Command line tool to interact with the DTrip Backend")

parser.add_argument(
    '--resync',
    nargs='?',
    const=True,
    help='Resync database'
)

parser.add_argument(
    '--swm',
    nargs='?',
    const=True,
    help='Sync SteemitWorldMap posts'
)

parser.add_argument(
    '--current',
    nargs='?',
    const=True,
    help='Stream from current block'
)

parser.add_argument('--block', type=int)
args = parser.parse_args()

if args.block:
    set_check_point('last_block', args.block)

if args.resync:
    set_check_point('accounts', 1)

    with suppress(KeyboardInterrupt):
        update_all_accounts()

if args.swm:
    with suppress(KeyboardInterrupt):
        update_swm_posts()

if args.current:
    set_check_point('last_block', get_current_block_num())

try:
    stream()
except KeyboardInterrupt:
    print('Exit...\n')
    exit()
