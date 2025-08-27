"""Contains constants for the program."""

# pylint: disable=too-few-public-methods

import pathlib


# Number of stars in route
NUM_STARS_IN_ROUTE = 70


# Keys
class ConfigKeys:
    """Contains keys for the user configuration file."""

    HUNDRED_COIN_TIMES_TABLE = "hundred_coin_times"
    HUNDRED_COIN_COMBINED_WITH = "combined_with"
    HUNDRED_COIN_TIMES = "times"
    PREREQUISITES_TABLE = "prerequisites"
    TIMES_TABLE = "times"


class DataKeys:
    """Contains keys for the data in the course_data module."""

    COURSE_CASTLE_ID = "CASTLE"
    COURSE_DIRE_DIRE_DOCKS_ID = "DDD"
    COURSE_ID = "id"
    COURSE_NAME = "name"
    COURSE_NUMBER = "number"
    COURSE_STARS = "stars"
    STAR_DDD1_ID = "DDD1"
    STAR_DDD_100_ID = "DDD_100"
    STAR_ID = "id"
    STAR_LOCATION = "location"
    STAR_NAME = "name"
    STAR_NUM_STARS_REQUIRED = "num_stars_required"
    STAR_NUMBER = "number"


# Castle locations
class Locations:
    """Contains castle location names.

    The following is a list of what each location name refers to:

    lobby: The first floor containing Bob-omb Battlefield, Bowser in the
      Dark World, etc.
    courtyard: The courtyard area which only includes Big Boo's Haunt.
    basement: The basement including Lethal Lava Land, Bowser in the
      Fire Sea, etc. This includes the vanish cap stage under the moat.
    upstairs: The second floor including Snowman's Land, Wet-Dry World,
      etc.
    tippy: The third floor including Tick Tock Clock, the "Wing Mario
      Over the Rainbow" castle star stage, etc.
    """

    BASEMENT = "basement"
    COURTYARD = "courtyard"
    LOBBY = "lobby"
    TIPPY = "tippy"
    UPSTAIRS = "upstairs"


ALL_LOCATIONS = {
    Locations.BASEMENT,
    Locations.COURTYARD,
    Locations.LOBBY,
    Locations.TIPPY,
    Locations.UPSTAIRS,
}
UPPER_LEVEL_LOCATIONS = {Locations.TIPPY, Locations.UPSTAIRS}


# Indices for star time tuples lists
# STAR_TIME_TUPLE_TIME_INDEX = 0
STAR_TIME_TUPLE_STAR_ID_INDEX = 1

# Paths
REPOSITORY_ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
DESTINATION_DIR = REPOSITORY_ROOT_DIR / "routes"
EXAMPLE_CONFIG_FILE = REPOSITORY_ROOT_DIR / "config.toml.example"
EXPECTED_CONFIG_FILE = REPOSITORY_ROOT_DIR / "config.toml"
