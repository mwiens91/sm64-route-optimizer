#!/usr/bin/env python3
"""Entry point for the program."""

import logging
import pathlib
import sys


# Add the src folder to the path
sys.path.append(str(pathlib.Path(__file__).resolve().parent / "src"))

# Import from src

# pylint: disable=wrong-import-position
from src.main import main
from src.exceptions import (
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
