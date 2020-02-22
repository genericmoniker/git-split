import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from gitsplit import log
from gitsplit.config import Config, ConfigError
from gitsplit.split import do_splits

# Fixed in pylint 2.5: https://github.com/PyCQA/pylint/issues/3111
logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def main() -> None:
    args = parse_args()
    log.setup()
    config_file = Path(args.config_file)
    try:
        config = Config.from_file(config_file)
    except (OSError, ConfigError) as ex:
        logger.error("Error reading config file: %s", ex)
        sys.exit(1)
    do_splits(config)


def parse_args():
    parser = ArgumentParser(description="A history-preserving file splitter for Git.")
    parser.add_argument(
        "config_file", metavar="CONFIG-FILE", help="TOML file defining split",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
