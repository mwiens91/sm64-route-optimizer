"""Contains functions for getting user configuration for the program."""

import logging
import pathlib
import tomllib
from cerberus import Validator
from src.constants import ConfigKeys, DataKeys, EXAMPLE_CONFIG_FILE
from src.exceptions import ConfigFileInvalid, ConfigFileNotFound
from src import util


# Set up logging for this module
logger = logging.getLogger(__name__)


# Schema for config data
NON_100_COIN_STARS = util.get_star_ids(include_all_possible_100_coin_stars=False)

CONFIG_DATA_SCHEMA = {
    ConfigKeys.TIMES_TABLE: {
        "type": "dict",
        "keysrules": {
            "type": "string",
            "allowed": NON_100_COIN_STARS,
        },
        "valuesrules": {"type": "list", "schema": {"type": "float"}},
    },
    ConfigKeys.HUNDRED_COIN_TIMES_TABLE: {
        "type": "dict",
        "keysrules": {
            "type": "string",
            "allowed": util.get_all_possible_100_coin_star_ids(),
        },
        "valuesrules": {
            "type": "dict",
            "schema": {
                ConfigKeys.HUNDRED_COIN_TIMES: {
                    "type": "list",
                    "schema": {"type": "float"},
                },
                ConfigKeys.HUNDRED_COIN_COMBINED_WITH: {
                    "type": "string",
                    "allowed": util.get_star_ids(
                        include_all_possible_100_coin_stars=False,
                        include_castle_stars=False,
                    ),
                },
            },
        },
    },
    ConfigKeys.PREREQUISITES_TABLE: {
        "type": "dict",
        "keysrules": {"type": "string", "allowed": NON_100_COIN_STARS},
        "valuesrules": {
            "type": "list",
            "schema": {"type": "string", "allowed": NON_100_COIN_STARS},
        },
    },
}


def get_and_validate_config(
    target_config_path: pathlib.Path, generate_fake_times: bool = False
) -> dict[str, dict]:
    """Get user config data and validate it.

    If we are generating fake times and the target config file does not
    exist, we use the example config file instead. This is useful for
    testing/development purposes.

    Args:
        target_config_path: The path where we expect to find the user
          configuration data.
        generate_fake_times: A flag for the program to generate fake
          times for each star.

    Returns:
        A dictionary containing the user's configuration data.

    Raises:
        ConfigFileInvalid: If the config data was invalid.
        ConfigFileNotFound: If we could not find a valid configuration
          file.
    """
    # Get the user configuration data (either the target or the example
    # config)
    if target_config_path.is_file():
        config_file = target_config_path
    else:
        # Target not found. If we are generating fake times, try using
        # the example config.
        if generate_fake_times:
            if EXAMPLE_CONFIG_FILE.is_file():
                logger.info(
                    "Could not find config file at %s. Using example config file.",
                    target_config_path,
                )

                config_file = EXAMPLE_CONFIG_FILE
            else:
                # No example config found
                raise ConfigFileNotFound(
                    f"Could not find user config data at {target_config_path}"
                    f" or example config data at {EXAMPLE_CONFIG_FILE}."
                )
        else:
            # Not generating fake times, so this is an error
            raise ConfigFileNotFound(
                f"Could not find user config data at {target_config_path}."
                f" Copy the example config {EXAMPLE_CONFIG_FILE} to {target_config_path}"
                " and add times."
            )

    # Read in config data
    with open(config_file, "rb") as f:
        config_data = tomllib.load(f)

    # Validate data
    validator = Validator(CONFIG_DATA_SCHEMA)

    if not validator.validate(config_data):
        # TODO: format this output better
        raise ConfigFileInvalid(
            f"Config at {target_config_path} is invalid due to the following schema errors: "
            + str(validator.errors)
        )

    # If we aren't generating fake times, ensure times for either DDD1
    # or DDD_100 combined with DDD1 are present
    #
    # NOTE: there is some redundancy in including this check given the
    # very similar validation check in the main module. Including both
    # checks allows the main module code to be more straightforward
    # however: here we're making sure the config file is valid, and
    # given that it is valid, the main module only needs to worry about
    # the excluded star IDs being valid.
    if not generate_fake_times:
        # Check whether DDD1 has times first.
        regular_star_times = config_data[ConfigKeys.TIMES_TABLE]

        ddd1_okay = (
            DataKeys.STAR_DDD1_ID in regular_star_times
            and regular_star_times[DataKeys.STAR_DDD1_ID]
        )

        # Now check whether DDD_100 and is combined with DDD1 and has times
        hundred_coin_times = config_data[ConfigKeys.HUNDRED_COIN_TIMES_TABLE]

        ddd_100_okay = (
            DataKeys.STAR_DDD_100_ID in hundred_coin_times
            and hundred_coin_times[DataKeys.STAR_DDD_100_ID][
                ConfigKeys.HUNDRED_COIN_COMBINED_WITH
            ]
            == DataKeys.STAR_DDD1_ID
            and hundred_coin_times[DataKeys.STAR_DDD_100_ID][ConfigKeys.HUNDRED_COIN_TIMES]
        )

        if not ddd1_okay and not ddd_100_okay:
            raise ConfigFileInvalid(
                f"No times found for {DataKeys.STAR_DDD1_ID} or a 100 coin alternative"
            )

    return config_data
