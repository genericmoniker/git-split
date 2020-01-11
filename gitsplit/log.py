import logging
import sys


def setup():
    logging.basicConfig(format="%(message)s", level=logging.INFO, stream=sys.stdout)
