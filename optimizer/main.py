"""Contains the main function for the program."""

from datetime import datetime
import json
import logging
import random
from .args import get_runtime_args
from .config import get_and_validate_config
from .constants import ConfigKeys, DataKeys, NUM_STARS_IN_ROUTE, DESTINATION_DIR
from .exceptions import InvalidExcludedStarIds
from .optimize import get_optimal_route
from . import util


# Set up logging for this module
logger = logging.getLogger(__name__)


def main() -> None:
    """Generate a JSON file containing an optimal 70 star route."""
    # Get runtime arguments and config data
    args = get_runtime_args()
    config_data = get_and_validate_config(
        target_config_path=args.config, generate_fake_times=args.generate_fake_times
    )

    # Get tuples (average_time, star_id) for stars which have times
    config_100_coin_times = config_data[ConfigKeys.HUNDRED_COIN_TIMES_TABLE]

    star_time_tuples = util.get_star_time_tuples(
        star_times_list_dict=util.get_star_times_list_dict(
            config_times=config_data[ConfigKeys.TIMES_TABLE],
            config_100_coin_times=config_100_coin_times,
        ),
        generate_fake_times=args.generate_fake_times,
    )

    # Build a dictionary of star times
    star_times_dict = util.build_star_times_dict_from_star_time_tuples(star_time_tuples)

    # Ensure at least one of the following is true:
    #
    # - DDD1 has a time and is not excluded
    # - DDD_100 is combined with DDD1 and has a time and is not excluded
    #
    # Note that a validation check in the configuration module has
    # already ensured that one of DDD1 or DDD_100 combined with DDD1 has
    # a time, so any error here is due to excluded star IDs.
    excluded_star_ids = set(args.exclude_star_ids)

    ddd1_okay = (
        DataKeys.STAR_DDD1_ID in star_times_dict
        and DataKeys.STAR_DDD1_ID not in excluded_star_ids
    )

    ddd_100_okay = (
        DataKeys.STAR_DDD_100_ID in star_times_dict
        and config_data[ConfigKeys.HUNDRED_COIN_TIMES_TABLE][DataKeys.STAR_DDD_100_ID][
            ConfigKeys.HUNDRED_COIN_COMBINED_WITH
        ]
        == DataKeys.STAR_DDD1_ID
        and DataKeys.STAR_DDD_100_ID not in excluded_star_ids
    )

    if not ddd1_okay and not ddd_100_okay:
        raise InvalidExcludedStarIds(
            f"Times exist for {DataKeys.STAR_DDD1_ID} (or its 100 coin alternative)"
            " but all have been excluded."
        )

    # Get course data with star count requirements adjusted according to
    # prerequisite relationships and with 100 coin stars added in
    prerequisites_dict = config_data[ConfigKeys.PREREQUISITES_TABLE]

    processed_course_data = util.adjust_and_augment_course_data(
        prerequisites_dict=prerequisites_dict,
        config_100_coin_times=config_100_coin_times,
    )

    # Get 70 stars which form an optimal route. Generate a non-optimal
    # random route if we were asked to do so; otherwise generate an
    # optimal route.
    if args.generate_fake_route:
        route_star_ids_set = random.sample(
            list(star_times_dict.keys()), NUM_STARS_IN_ROUTE
        )
        route_time = sum(star_times_dict[star_id] for star_id in route_star_ids_set)
    else:
        logger.info(
            "Finding optimal route. This should take a few seconds—no longer than a few minutes.",
        )

        # Perform the actual algorithm
        route_star_ids_set, route_time = get_optimal_route(
            star_time_tuples=util.filter_star_time_tuples(
                star_time_tuples=star_time_tuples,
                excluded_course_ids=set(args.exclude_course_ids),
                excluded_star_ids=excluded_star_ids,
            ),
            max_num_upper_level_stars=args.max_upper_level_stars,
            adjacency_list_dict=util.get_adjacency_list_dict_from_prerequisites_dict(
                prerequisites_dict=prerequisites_dict
            ),
            base_star_alts_dict=util.build_base_star_alts_dict(
                config_100_coin_times=config_100_coin_times
            ),
            star_locations_dict=util.build_star_locations_dict(
                course_data=processed_course_data
            ),
            num_stars_required_dict=util.build_num_stars_required_dict(
                course_data=processed_course_data
            ),
        )

    # Log the time the optimal route takes
    route_minutes, route_remaining_seconds = (
        util.convert_seconds_to_minutes_and_remaining_seconds(route_time)
    )

    if route_minutes:
        logger.info(
            "Optimal route found: sum of star times = %d minutes %.2f seconds.",
            route_minutes,
            route_remaining_seconds,
        )
    else:
        logger.info(
            "Optimal route found: sum of star times = %.2f seconds.",
            route_remaining_seconds,
        )

    # Output route to JSON
    DESTINATION_DIR.mkdir(exist_ok=True)

    # TODO: make a function to sort the route star ids set
    # TODO: put times and route stars in included dict
    data = dict(
        route_star_ids=route_star_ids_set,
        route_time=route_time,
        num_stars_per_location_dict=util.build_num_stars_per_location_dict(
            route_star_ids=route_star_ids_set, course_data=processed_course_data
        ),
        num_stars_per_course_dict=util.build_num_stars_per_course_dict(
            route_star_ids=route_star_ids_set, course_data=processed_course_data
        ),
        star_times_dict=star_times_dict,
        course_data=processed_course_data,
    )
    output_path = (
        DESTINATION_DIR / f"{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json"
    )
    output_path.write_text(json.dumps(data, indent=2))
