#!/usr/bin/env python3
"""Entry point for the program."""

import logging
import pathlib
import sys


# Add the optimizer folder to the path
sys.path.append(str(pathlib.Path(__file__).resolve().parent / "optimizer"))

# Import from optimizer

# pylint: disable=wrong-import-position
from optimizer.main import main
from optimizer.exceptions import (
    ConfigFileInvalid,
    ConfigFileNotFound,
    InvalidExcludedStarIds,
    NoValidRoutePossible,
)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        main()
    except (
        ConfigFileNotFound,
        ConfigFileInvalid,
        InvalidExcludedStarIds,
        NoValidRoutePossible,
    ) as e:
        logging.critical(str(e))

        sys.exit(1)
