"""Contains a functionality to handle runtime arguments."""

import argparse
import pathlib
from .constants import DataKeys, EXPECTED_CONFIG_FILE, NUM_STARS_IN_ROUTE
from . import util


def get_runtime_args() -> argparse.Namespace:
    """Get runtime arguments.

    Returns:
        A namespace containing values for the runtime arguments.
    """
    # Set up parser
    parser = argparse.ArgumentParser(
        prog="sm64-route-optimizer",
        description="Get optimal 70 star routes using Super Mario 64 user time data",
    )
    parser.add_argument(
        "--config",
        help=f"use given config TOML file (defaults to {EXPECTED_CONFIG_FILE})",
        type=pathlib.Path,
        default=EXPECTED_CONFIG_FILE,
    )
    parser.add_argument(
        "--exclude-course-ids",
        help="exclude given course IDs from being included in route",
        metavar="COURSE_ID",
        nargs="*",
        choices=util.get_course_ids() - {DataKeys.COURSE_DIRE_DIRE_DOCKS_ID},
        default=[],
    )
    parser.add_argument(
        "--exclude-star-ids",
        help="exclude given star IDs from being included in route",
        metavar="STAR_ID",
        nargs="*",
        choices=util.get_star_ids(),
        default=[],
    )
    parser.add_argument(
        "--max-upper-level-stars",
        help="set maximum number of stars from upstairs and tippy to"
        " include in the route",
        type=int,
        default=NUM_STARS_IN_ROUTE,
    )
    # NOTE: Use this in development to get output without having
    # sufficient data
    parser.add_argument(
        "-g",
        "--generate-fake-times",
        help="generate a route using randomly generated star times"
        " (uses logic from example config file if user config does does not exist)",
        action="store_true",
    )
    # NOTE: Use this in development to get output quickly
    parser.add_argument(
        "-f",
        "--generate-fake-route",
        help=f"generate a route with {NUM_STARS_IN_ROUTE} randomly chosen stars"
        " (no logic or optimization)",
        action="store_true",
    )

    # Parse arguments
    return parser.parse_args()
