import logging
import sys
from argparse import ArgumentParser
from contextlib import ExitStack
from pathlib import Path

from gitsplit import log
from gitsplit.config import Config, ConfigError

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

    with ExitStack() as stack:
        # Working around pylint bug: https://github.com/PyCQA/pylint/issues/3137
        sfs = config.split_files
        splits = [stack.enter_context(sf) for sf in sfs]  # pylint:disable=no-member
        for line_number, line in enumerate(config.source_file.lines, start=1):
            for split_file in splits:
                if line_number in split_file:
                    split_file.write(line)


def parse_args():
    parser = ArgumentParser(description="A history-preserving file splitter for Git.")
    parser.add_argument(
        "config_file", metavar="CONFIG-FILE", help="TOML file defining split",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
