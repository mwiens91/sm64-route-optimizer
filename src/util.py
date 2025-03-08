"""Contains utility functions for the program."""

from collections.abc import Iterable
import copy
import functools
import random
import re
import statistics
from src.constants import ALL_LOCATIONS, ConfigKeys, DataKeys
from src.course_data import COURSES


def get_course_ids(include_castle: bool = True) -> set[str]:
    """Get a set of course IDs.

    Args:
        include_castle: Flag to include the CASTLE ID. It's special in
          that it isn't really a course, but for simplicity is referred
          to one throughout most of the program.

    Returns:
        A set of course IDs.
    """
    course_ids = set()

    for course in COURSES:
        if (
            course_id := course[DataKeys.COURSE_ID]
        ) != DataKeys.COURSE_CASTLE_ID or include_castle:
            course_ids.add(course_id)

    return course_ids


def get_all_possible_100_coin_star_ids() -> set[str]:
    """Get a set of all possible 100 coin star IDs.

    Returns:
        A set of all possible 100 coin star IDs.
    """
    return {course_id + "_100" for course_id in get_course_ids(include_castle=False)}


def get_star_ids(
    include_all_possible_100_coin_stars: bool = True, include_castle_stars: bool = True
) -> set[str]:
    """Get a set of star IDs.

    Args:
        include_all_possible_100_coin_stars: Flag to include all
          possible 100 coin star IDs, not just the the 100 coin star IDs
          listed in the user config data.
        include_castle_stars: Flag to include castle star IDs.

    Returns:
        A set of star IDs.
    """
    star_ids = set()

    # Add non-100 coin stars
    for course in COURSES:
        if (
            course[DataKeys.COURSE_ID] != DataKeys.COURSE_CASTLE_ID
            or include_castle_stars
        ):
            star_ids.update(
                {star[DataKeys.STAR_ID] for star in course[DataKeys.COURSE_STARS]}
            )

    # Add all possible 100 coin stars
    if include_all_possible_100_coin_stars:
        star_ids.update(get_all_possible_100_coin_star_ids())

    return star_ids


def get_course_id_from_star_id(star_id: str) -> str:
    """Get the course ID given a star ID.

    Args:
        star_id: A star ID.

    Returns:
        The passed in star's course's course ID.
    """
    return re.match(r"^[A-Z]+", star_id).group()


def get_star_times_list_dict(
    config_times: dict[str, list[float]],
    config_100_coin_times: dict[str, dict[str, list[float] | str]],
) -> dict[str, list[float]]:
    """Parse all star times from user data into a dictionary.

    Args:
        config_times: A dictionary of non-100 coin star times from the
          user's data.
        config_100_coin_times: A dictionary of 100 coin star times from
          the user's data.

    Returns:
        A dictionary containing star IDs as keys and a list of times as
        values.
    """
    star_times_list_dict = config_times.copy()

    for hundred_coin_star_id, hundred_coin_star_data in config_100_coin_times.items():
        star_times_list_dict[hundred_coin_star_id] = hundred_coin_star_data[
            ConfigKeys.HUNDRED_COIN_TIMES
        ]

    return star_times_list_dict


def get_star_time_tuples(
    star_times_list_dict: dict[str, list[float]],
    generate_fake_times: bool = False,
) -> list[tuple[float, str]]:
    """Construct a list of (average_time, star_id) tuples for stars with times.

    Only stars which contain times are included in the output list,
    unless the generate_fake_times flag is true, in which case the
    average_time is just a randomly generated time for all stars.

    Args:
        star_times_list_dict: A dictionary containing star IDs as keys
          and a list of times as values.
        generate_fake_times: A flag for the program to generate fake
          times for each star.

    Returns:
        A list of two-tuples for stars with times containing the average
        time that a star takes (or a randomly generated time if this was
        specified) as the first element and that star's ID as the second
        element.
    """
    star_time_tuples = []

    for star_id, times in star_times_list_dict.items():
        if generate_fake_times:
            average_time = 60 + max(-50, random.gauss(sigma=20))
        elif times:
            average_time = statistics.fmean(times)
        else:
            # No times
            continue

        star_time_tuples.append((average_time, star_id))

    return star_time_tuples


def filter_star_time_tuples(
    star_time_tuples: Iterable[tuple[float, str]],
    excluded_course_ids: set[str],
    excluded_star_ids: set[str],
) -> list[tuple[float, str]]:
    """Filter out stars from star time tuples.

    Args:
        star_time_tuples: An iterable of tuples (time, star_id) where
            star_ids are star IDs eligible to be in a route and time is
            the time a star takes.
        excluded_course_ids: A set containing course IDs to exclude.
        excluded_star_ids: A set containing star IDs to exclude.

    Returns:
        A list of star time tuples filtered to exclude stars with given
        course IDs or star IDs.
    """
    new_star_time_tuples = []

    for time, star_id in star_time_tuples:
        if (
            get_course_id_from_star_id(star_id) not in excluded_course_ids
            and star_id not in excluded_star_ids
        ):
            new_star_time_tuples.append((time, star_id))

    return new_star_time_tuples


def build_star_times_dict_from_star_time_tuples(
    star_time_tuples: Iterable[tuple[float, str]]
) -> dict[str, float]:
    """Build a dictionary with star IDs as keys and times as values.

    Args:
        star_time_tuples: An iterable of tuples (time, star_id) where
            star_ids are star IDs eligible to be in a route and time is
            the time a star takes.

    Returns:
        A dictionary containing star IDs as keys and times as values
    """
    return {star_id: time for time, star_id in star_time_tuples}


def build_base_star_alts_dict(
    config_100_coin_times: dict[str, dict[str, list[float] | str]]
) -> dict[str, str]:
    """Build a dictionary with 100 coin star alternatives for base stars.

    Args:
        config_100_coin_times: A dictionary of 100 coin star times from
          the user's data.

    Returns:
        A dictionary with base star IDs as keys and 100 coin star IDs
        that can be used to replace the base star as values.
    """
    base_star_alts_dict = {}

    for hundred_coin_star_id, hundred_coin_star_data in config_100_coin_times.items():
        base_star_alts_dict[
            hundred_coin_star_data[ConfigKeys.HUNDRED_COIN_COMBINED_WITH]
        ] = hundred_coin_star_id

    return base_star_alts_dict


def get_adjacency_list_dict_from_prerequisites_dict(
    prerequisites_dict: dict[str, list[str]]
) -> dict[str, list[str]]:
    """Build a dictionary of adjacency lists from prerequisite data.

    Args:
        prerequisites_dict: A dictionary which has star IDs as keys and
          a list of prerequisite IDs as values.

    Returns:
        A dictionary which has star IDs as keys and non-empty lists of
          star IDs the key star is a prerequisite for as values.
    """
    adjacency_list_dict = {}

    for dependant, prerequisites in prerequisites_dict.items():
        for prerequisite in prerequisites:
            try:
                adjacency_list_dict[prerequisite].append(dependant)
            except KeyError:
                adjacency_list_dict[prerequisite] = [dependant]

    return adjacency_list_dict


def build_num_stars_required_dict(course_data: list[dict]) -> dict[str, int]:
    """Build a dictionary which enumerates the star count requirements.

    Args:
        course_data: Course data coming from the course_data module or
          after being processed to adjust star count requirements and
          add in 100 coin stars from user data.

    Returns:
        A dictionary which has star IDs as keys and the star count they
        require as values.
    """
    num_stars_required_dict = {}

    for course in course_data:
        for star in course[DataKeys.COURSE_STARS]:
            num_stars_required_dict[star[DataKeys.STAR_ID]] = star[
                DataKeys.STAR_NUM_STARS_REQUIRED
            ]

    return num_stars_required_dict


def build_star_locations_dict(course_data: list[dict]) -> dict[str, int]:
    """Build a dictionary which contains each star's location.

    Args:
        course_data: Course data coming from the course_data module or
          after being processed to adjust star count requirements and add
          in 100 coin stars from user data.

    Returns:
        A dictionary which has star IDs as keys and their locations as
        values.
    """
    star_locations_dict = {}

    for course in course_data:
        for star in course[DataKeys.COURSE_STARS]:
            star_locations_dict[star[DataKeys.STAR_ID]] = star[DataKeys.STAR_LOCATION]

    return star_locations_dict


def adjust_course_data_star_count_requirements_from_prerequisites(
    prerequisites_dict: dict[str, list[str]]
) -> list[dict]:
    """Adjust course data star count requirements using prerequisites.

    This returns a new copy of the course data. Note that this is *not*
    compatible with 100 coin stars in the course data; these stars
    should be added after running this function.

    Args:
        prerequisites_dict: A dictionary which has star IDs as keys and
          a list of prerequisite IDs as values.

    Returns:
        A copy of the course data from the course_data module with star
        count requirements adjusted based on the greatest star count
        requirement of any ancestor.
    """
    num_stars_required_dict = build_num_stars_required_dict(COURSES)

    @functools.cache
    def _find_true_star_count_requirement(star_id: str) -> int:
        """Find the star count requirement of a star given its prerequisites.

        Args:
            star_id: The ID of the star we're processing.

        Returns:
            The highest star count requirement among the passed in star
            and any of its ancestors.
        """
        if star_id not in prerequisites_dict or not prerequisites_dict[star_id]:
            # No ancestors, just use current star count requirement
            return num_stars_required_dict[star_id]

        return max(
            num_stars_required_dict[star_id],
            *[
                _find_true_star_count_requirement(prerequisite_id)
                for prerequisite_id in prerequisites_dict[star_id]
            ],
        )

    # Modify the number of stars required for each star which has
    # prerequisites
    course_data_copy = copy.deepcopy(COURSES)

    for course in course_data_copy:
        for star in course[DataKeys.COURSE_STARS]:
            star_id = star[DataKeys.STAR_ID]

            if star_id in prerequisites_dict:
                star[DataKeys.STAR_NUM_STARS_REQUIRED] = (
                    _find_true_star_count_requirement(star_id)
                )

    return course_data_copy


def augment_course_data_with_user_100_coin_stars(
    course_data: list[dict],
    config_100_coin_times: dict[str, dict[str, list[float] | str]],
) -> list[dict]:
    """Augment course data with user listed 100 coin stars.

    This returns a new copy of the course data. Note that this does not
    include all possible 100 coin stars—only the ones listed in the user
    config data.

    Args:
        course_data: Course data coming from the course_data module.
          This data should already have the star requirements adjusted
          using functions in this (util) module.
        config_100_coin_times: A dictionary of 100 coin star times from
          the user's data.

    Returns:
        A copy of the passed in course data with user listed 100 coin
        stars included.
    """
    course_data_copy = copy.deepcopy(course_data)

    for hundred_coin_star_id, hundred_coin_star_data in config_100_coin_times.items():
        # Get course's star list that we want to insert this star into
        course_id = get_course_id_from_star_id(hundred_coin_star_id)
        course = next(d for d in course_data_copy if d[DataKeys.COURSE_ID] == course_id)
        course_star_list = course[DataKeys.COURSE_STARS]

        # Find the star that the 100 coin star is combined with
        combined_with_star_id = hundred_coin_star_data[
            ConfigKeys.HUNDRED_COIN_COMBINED_WITH
        ]
        combined_with_star = next(
            d for d in course_star_list if d[DataKeys.STAR_ID] == combined_with_star_id
        )

        # Add the hundred coin star to the course's star data
        hundred_coin_star = combined_with_star.copy()

        hundred_coin_star[DataKeys.STAR_ID] = hundred_coin_star_id
        hundred_coin_star[DataKeys.STAR_NUMBER] = 7
        hundred_coin_star[DataKeys.STAR_NAME] = (
            combined_with_star[DataKeys.STAR_NAME] + " + 100 Coins Star"
        )

        course_star_list.append(hundred_coin_star)

    return course_data_copy


def adjust_and_augment_course_data(
    prerequisites_dict: dict[str, list[str]],
    config_100_coin_times: dict[str, dict[str, list[float] | str]],
) -> list[dict]:
    """Adjust the star count requirements and add in 100 coin stars to course data.

    This does not modify the course data; it returns a new copy.

    Args:
        prerequisites_dict: A dictionary which has star IDs as keys and
          a list of prerequisite IDs as values.
        config_100_coin_times: A dictionary of 100 coin star times from
          the user's data.

    Returns:
        A copy of the course data from the course_data module with star
        count requirements adjusted based on prerequisite relationships,
        and with 100 coin stars added in.
    """
    return augment_course_data_with_user_100_coin_stars(
        course_data=adjust_course_data_star_count_requirements_from_prerequisites(
            prerequisites_dict
        ),
        config_100_coin_times=config_100_coin_times,
    )


def convert_seconds_to_minutes_and_remaining_seconds(
    seconds: float,
) -> tuple[int, float]:
    """Convert seconds to minutes and remaining seconds.

    Args:
        seconds: The number of seconds to convert.

    Returns:
        A two-tuple containing (minutes, remaining seconds).
    """
    return (int(seconds // 60), seconds % 60)


def build_num_stars_per_location_dict(
    route_star_ids: set[str], course_data: list[dict]
) -> dict[str, int]:
    """Build a dictionary which enumerates each location's star count given a route.

    Args:
        route_star_ids: A set containing the star IDs in a route.
        course_data: Course data coming from the course_data module; the
          data should be augmented with the 100 coin stars listed in the
          user config data using functionality in the util module.

    Returns:
        A dictionary with locations as keys and the number of stars in
        the route from that location as values.
    """
    num_stars_per_location_dict = {location: 0 for location in ALL_LOCATIONS}

    hundred_coin_star_ids = get_all_possible_100_coin_star_ids()

    for course in course_data:
        for star in course[DataKeys.COURSE_STARS]:
            star_id = star[DataKeys.STAR_ID]

            if star_id in route_star_ids:
                star_increment = 2 if star_id in hundred_coin_star_ids else 1

                num_stars_per_location_dict[
                    star[DataKeys.STAR_LOCATION]
                ] += star_increment

    return num_stars_per_location_dict


def build_num_stars_per_course_dict(
    route_star_ids: set[str], course_data: list[dict]
) -> dict[str, int]:
    """Build a dictionary which enumerates each course's star count given a route.

    This includes all course IDs as keys, not just for courses for which
    the user has times.

    Args:
        route_star_ids: A set containing the star IDs in a route.
        course_data: Course data coming from the course_data module; the
          data should be augmented with the 100 coin stars listed in the
          user config data using functionality in the util module.

    Returns:
        A dictionary with course IDs as keys and the number of stars in
        the route from that course as values.
    """
    num_stars_per_course_dict = {}

    hundred_coin_star_ids = get_all_possible_100_coin_star_ids()

    for course in course_data:
        course_id = course[DataKeys.COURSE_ID]

        num_stars_per_course_dict[course_id] = 0

        for star in course[DataKeys.COURSE_STARS]:
            star_id = star[DataKeys.STAR_ID]

            if star_id in route_star_ids:
                star_increment = 2 if star_id in hundred_coin_star_ids else 1

                num_stars_per_course_dict[course_id] += star_increment

    return num_stars_per_course_dict
