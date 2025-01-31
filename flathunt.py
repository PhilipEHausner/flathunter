#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Flathunter - search for flats by crawling property portals, and receive telegram
   messages about them. This is the main command-line executable, for running on the
   console. To run as a webservice, look at main.py"""

import argparse
import os
import logging
import time
from pprint import pformat

from flathunter.idmaintainer import IdMaintainer
from flathunter.hunter import Hunter
from flathunter.config import Config

__author__ = "Jan Harrie"
__version__ = "1.0"
__maintainer__ = "Nody"
__email__ = "harrymcfly@protonmail.com"
__status__ = "Production"


def create_folder(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


# init logging
LOG_FORMAT = '[%(asctime)s|%(filename)-18s|%(levelname)-8s]: %(message)s'
create_folder("./logs")
logging.basicConfig(
    filename=os.path.join("logs", "flathunt.log"),
    filemode="w",
    format=LOG_FORMAT,
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO)
__log__ = logging.getLogger('flathunt')


def launch_flat_hunt(config):
    """Starts the crawler / notification loop"""
    id_watch = IdMaintainer('%s/processed_ids.db' % config.database_location())

    hunter = Hunter(config, id_watch)
    hunter.hunt_flats()

    while config.get('loop', dict()).get('active', False):
        time.sleep(config.get('loop', dict()).get('sleeping_time', 60 * 10))
        hunter.hunt_flats()


def main():
    """Processes command-line arguments, loads the config, launches the flathunter"""
    parser = argparse.ArgumentParser(description=\
             "Searches for flats on Immobilienscout24.de and wg-gesucht.de",
                                     epilog="Designed by Nody")
    parser.add_argument('--config', '-c',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        default='%s/config.yaml' % os.path.dirname(os.path.abspath(__file__)),
                        help="Config file to use. If not set, try to use '%s/config.yaml' " %
                        os.path.dirname(os.path.abspath(__file__))
                        )
    args = parser.parse_args()

    # load config
    config_handle = args.config
    config = Config(config_handle.name)

    # check config
    if not config.get('urls'):
        __log__.error("No urls configured. Starting like this would be meaningless...")
        return

    # adjust log level, if required
    if config.get('verbose'):
        __log__.setLevel(logging.DEBUG)
        __log__.debug("Settings from config: %s", pformat(config))

    # start hunting for flats
    launch_flat_hunt(config)


if __name__ == "__main__":
    main()
