"""Contains functionality to find an optimal 70 star route."""

import heapq
import itertools
import math
from src.constants import (
    ALL_LOCATIONS,
    DataKeys,
    NUM_STARS_IN_ROUTE,
    STAR_TIME_TUPLE_STAR_ID_INDEX,
    UPPER_LEVEL_LOCATIONS,
)
from src.exceptions import InsufficientRemainingStars, NoValidRoutePossible
from src.optimize_helpers import (
    find_descendants,
    get_topological_sort_of_prerequisites,
)
from src import util


def get_optimal_route(
    star_time_tuples: list[tuple[float, str]],
    max_num_upper_level_stars: int,
    adjacency_list_dict: dict[str, list[str]],
    base_star_alts_dict: dict[str, str],
    star_locations_dict: dict[str, str],
    num_stars_required_dict: dict[str, int],
) -> tuple[set[str], float]:
    """Find star IDs which form an optimal route.

    The general idea is to consider each valid way to partition special
    stars (prerequisites and base stars with 100 coin star alternatives,
    along with the 100 coin star alternatives that exist for either of
    those) into either being included in the route or being excluded
    from the route. For a given partition, we add stars which are not
    excluded and which we have the required star count for. We gather
    70 - max_num_upper_level_stars stars which are not on the upper
    levels first, then we get the remaining max_num_upper_level_stars
    from any location. We account for 100 coin stars by having each of
    them count as two stars towards the total.

    Args:
        star_time_tuples: A list of tuples (time, star_id) where
          star_ids are the star IDs eligible for the optimal route and
          time is the time a star takes.
        max_num_upper_level_stars: The maximum number of stars from the
          upper levels (upstairs and tippy) that can be added to the
          route.
        adjacency_list_dict: A dictionary which has non-100 coin star
          IDs as keys and non-empty lists of star IDs the key star is a
          prerequisite for as values.
        base_star_alts_dict: A dictionary with base star IDs as keys and
          100 coin star IDs that can be used to replace the base star as
          values.
        star_locations_dict: A dictionary which has star IDs as keys and
          their locations as values.
        num_stars_required_dict: A dictionary which has star IDs as keys
          and the star count they require as values.

    Returns:
        A two-tuple containing (1) the set containing the star IDs which
        are in the optimal route that was found and (2) the time an
        optimal route takes.

    Raises:
        NoValidRoutePossible: If we were unable to form any route due to
          insufficient time data.
    """
    # For each 100 coin star, half its time; we're going to treat them
    # as two stars with the same ID, each of which has half the time
    hundred_coin_star_ids = set(base_star_alts_dict.values())

    for idx, (_, star_id) in enumerate(star_time_tuples):
        if star_id in hundred_coin_star_ids:
            star_time_tuples[idx] = (
                star_time_tuples[idx][0] / 2,
                star_time_tuples[idx][1],
            )

    # Sort the star time tuples in order of increasing time
    star_time_tuples.sort()

    # Build a dictionary containing star IDs as keys and times as values
    star_times_dict = util.build_star_times_dict_from_star_time_tuples(star_time_tuples)

    # For each valid partitioning of the special stars, add valid stars
    # from shortest to longest until we reach the desired star total.
    # Keep track of the shortest total time and the star IDs that lead
    # to this total time.
    best_time = math.inf
    best_star_ids_set: set[str] | None = None

    for star_ids_set, excluded_set in get_valid_special_star_partitions(
        adjacency_list_dict,
        base_star_alts_dict,
        eligible_stars=set(star_times_dict.keys()),
    ):
        # Get the total time, star count, and number of upper level
        # stars for the stars already in the set
        starting_total_time = 0
        starting_star_count = 0
        num_upper_level_stars = 0

        for star_id in star_ids_set:
            mult = 2 if star_id in hundred_coin_star_ids else 1

            starting_total_time += mult * star_times_dict[star_id]
            starting_star_count += mult

            if star_locations_dict[star_id] in UPPER_LEVEL_LOCATIONS:
                num_upper_level_stars += 1

        # If we've exceeded the maximum number of upper level stars,
        # skip this iteration
        if num_upper_level_stars > max_num_upper_level_stars:
            continue

        # Now add stars from the star time tuples list until we reach
        # the desired count
        try:
            # Add in stars which aren't on the upper levels
            min_num_non_upper_level_stars = (
                NUM_STARS_IN_ROUTE - max_num_upper_level_stars
            )
            star_count_to_reach_from_non_upper_levels = (
                min_num_non_upper_level_stars + num_upper_level_stars
            )

            total_time, star_ids_set = add_non_special_stars_to_star_set(
                starting_total_time,
                starting_star_count,
                star_count_to_reach_from_non_upper_levels,
                ALL_LOCATIONS - UPPER_LEVEL_LOCATIONS,
                star_ids_set,
                excluded_set,
                star_time_tuples,
                hundred_coin_star_ids,
                star_locations_dict,
                num_stars_required_dict,
            )

            # Add in stars from anywhere
            total_time, star_ids_set = add_non_special_stars_to_star_set(
                total_time,
                max(starting_star_count, star_count_to_reach_from_non_upper_levels),
                NUM_STARS_IN_ROUTE,
                ALL_LOCATIONS,
                star_ids_set,
                excluded_set,
                star_time_tuples,
                hundred_coin_star_ids,
                star_locations_dict,
                num_stars_required_dict,
            )

            # Update best time and stars set
            if total_time < best_time:
                best_time = total_time
                best_star_ids_set = star_ids_set

        except InsufficientRemainingStars:
            pass

    # Return stars IDs which form an optimal route
    if best_star_ids_set is not None:
        return (best_star_ids_set, best_time)

    raise NoValidRoutePossible(
        f"Unable to form any {NUM_STARS_IN_ROUTE} star route due "
        "to insufficient eligible stars."
    )


def add_non_special_stars_to_star_set(
    starting_time: float,
    starting_star_count: int,
    max_star_count: int,
    allowed_locations: set[str],
    included_set: set[str],
    excluded_set: set[str],
    star_time_tuples: list[tuple[float, str]],
    hundred_coin_star_ids: set[str],
    star_locations_dict: dict[str, str],
    num_stars_required_dict: dict[str, int],
) -> tuple[float, set[str]]:
    """
    Add non-special star IDs to a star ID set.

    The strategy here is iterate until we reach the desired number of
    stars. First we try to look for a star to add from a min-heap that
    we meet the required star count for (the heap is ordered on required
    star count). If there is no such star on the heap, we look at the
    sorted star time tuples list: any stars which are not already
    included or excluded and have an allowed location that we do not
    meet the required star for count are added to the heap; we continue
    until we find a valid star we meet the required star count for. We
    then move to the next iteration, keeping track of what index we were
    last at in the star time tuples list.

    Args:
        starting_time: The time taken by the stars initially included in
          the included set.
        starting_star_count: The star count of the stars initially
          included in the included set.
        max_star_count: The maximum number of stars to get.
        allowed_locations: A set of locations for which we can add stars
          from.
        included_set: A set of star IDs that are included in the route.
        excluded_set: A set of star IDs that are excluded from the
          route.
        star_time_tuples: A list of tuples (time, star_id) where
          star_ids are the star IDs eligible for the optimal route and
          time is the time a star takes.
        hundred_coin_star_ids: A set of 100 coin star IDs.
        star_locations_dict: A dictionary which has star IDs as keys and
          their locations as values.
        num_stars_required_dict: A dictionary which has star IDs as keys
          and the star count they require as values.

    Returns:
        A two-tuple containing the total time taken by the stars in the
        route, and a set of star IDs included in the route.

    Raises:
        InsufficientRemainingStars: If there weren't enough remaining
          stars to finish forming the route.
    """
    total_time = starting_time
    star_count = starting_star_count

    # Make min-heap holding tuples (stars_required, star_time_tuple)
    # (where star_time_tuple is a two-tuple (time, star_id))
    STAR_REQUIREMENT_INDEX = 0  # pylint: disable=invalid-name

    heap: list[tuple[int, tuple[float, str]]] = []

    # Keep track of index in star time tuples list
    star_time_tuples_idx = 0

    # Add in stars until we have the required number
    while star_count < max_star_count:
        star_time_tuple_to_add: tuple[float, str] | None = None

        # Try adding from the heap
        if heap and heap[0][STAR_REQUIREMENT_INDEX] <= star_count:
            _, star_time_tuple_to_add = heapq.heappop(heap)

        # Try adding from the star time tuples list
        while star_time_tuple_to_add is None:
            try:
                star_time_tuple = star_time_tuples[star_time_tuples_idx]
            except IndexError as e:
                # Ran out of isolated stars
                raise InsufficientRemainingStars from e

            # Increment index for next iteration
            star_time_tuples_idx += 1

            # Skip this star ID if it's already included or excluded or
            # if it's from an unallowed location
            star_id = star_time_tuple[STAR_TIME_TUPLE_STAR_ID_INDEX]

            if (
                star_id in included_set
                or star_id in excluded_set
                or star_locations_dict[star_id] not in allowed_locations
            ):
                continue

            # If we meet the required star count, add this star;
            # otherwise throw it on the heap
            if (num_stars_required := num_stars_required_dict[star_id]) <= star_count:
                star_time_tuple_to_add = star_time_tuple
            else:
                # Not enough stars required. Add it to the heap.
                heapq.heappush(heap, (num_stars_required, star_time_tuple))

        # Unpack the star to add
        time_to_add, star_id_to_add = star_time_tuple_to_add

        # Add to star IDs set
        included_set.add(star_id_to_add)

        # Add to total time, star count, and number of upper level
        # stars
        mult = 2 if star_id_to_add in hundred_coin_star_ids else 1

        total_time += mult * time_to_add
        star_count += mult

    return (total_time, included_set)


def get_valid_special_star_partitions(
    adjacency_list_dict: dict[str, list[str]],
    base_star_alts_dict: dict[str, str],
    eligible_stars: set[str],
) -> list[tuple[set[str], set[str]]]:
    """Return a list of special star IDs partitioned into two disjoint sets.

    The special stars are prerequisite stars and base stars which have
    100 coin star alternatives along with those 100 coin star
    alternatives. The disjoint sets are of stars to be included and
    stars to be excluded, and the partitioning is valid under the
    prerequisite relationships given by the adjacency lists and the
    mutual exclusivity relationships introduced by the 100 coin star
    alternatives.

    Since DDD1 needs to be in the route, we initialize the route
    including it (or its 100 coin star alternative, if that exists).
    Important note: we make a critical assumption here that DDD1 has *no
    ancestors*. It's relatively simple to programmatically find any, but
    also there's no reason why you would ever want DDD1 to have
    ancestors, so ancestors are not considered.

    Args:
        adjacency_list_dict: A dictionary which has non-100 coin star
          IDs as keys and non-empty lists of star IDs the key star is a
          prerequisite for as values.
        base_star_alts_dict: A dictionary with base star IDs as keys and
          100 coin star IDs that can be used to replace the base star as
          values.
        eligible_stars: A set containing star IDs which are eligible to
          be in the route.

    Returns:
        A list of two-tuples, each containing a partitioning of special
        star IDs to be included (the set in the first element of the
        tuple) and to be excluded (the set in the second element), where
        the excluded set also includes non-special star IDs which need
        to be excluded as a consequence of the partitioning scheme.
    """
    # Get an ordering of base star special star IDs which contain,
    # first, a topologically sorted list of base star prerequisite star
    # IDs, and then, after, the remaining base star IDs with 100 coin
    # star alternatives
    sorted_base_star_prerequisite_ids = get_topological_sort_of_prerequisites(
        adjacency_list_dict
    )
    remaining_base_stars_with_alternatives = [
        base_star
        for base_star in base_star_alts_dict
        if base_star not in adjacency_list_dict
    ]
    ordered_base_special_stars = (
        sorted_base_star_prerequisite_ids + remaining_base_stars_with_alternatives
    )

    # Put valid partitions in here
    valid_partitions: list[tuple[set[str], set[str]]] = []

    def _get_star_and_alternative_id_pairs(
        base_star_id: str, excluded_star_id_set: set[str]
    ) -> list[tuple[str, str | None]]:
        """Returns pairings of a base star ID and its 100 coin alternative ID.

        The idea here is that we want to iterative over tuples, given a
        base star, containing first the base star ID and, second, the
        100 coin star alternative ID; and also the other way around. The
        first element of each two-tuple is always an eligible star. If a
        star does not have an eligible alternative but is itself
        eligible, the alternative ID is None and the output contains a
        single pair (star, alternative). If neither the base star nor
        the 100 coin alternative are eligible, the output is an empty
        list.

        Args:
            base_star_id: The base star ID to get pairings for.
            excluded_star_id_set: A set of excluded star IDs.

        Returns:
            A list of tuples containing base star ID and 100 coin
            alternative ID pairings subject to their existence and
            eligibility.
        """
        # Get the 100 coin alternative ID (or set it to None if it
        # doesn't exist or isn't eligible)
        if (
            base_star_id in base_star_alts_dict
            and base_star_alts_dict[base_star_id] in eligible_stars
            and base_star_alts_dict[base_star_id] not in excluded_star_id_set
        ):
            hundred_coin_alternative_star_id = base_star_alts_dict[base_star_id]
        else:
            hundred_coin_alternative_star_id = None

        # Replace the base star ID with None if it isn't eligible
        if base_star_id not in eligible_stars or base_star_id in excluded_star_id_set:
            base_star_id = None

        # Build the output
        pairs = []

        for main_id, alternative_id in itertools.permutations(
            (base_star_id, hundred_coin_alternative_star_id)
        ):
            if main_id is not None:
                pairs.append((main_id, alternative_id))

        return pairs

    def _generate_valid_partitions_recursive(
        star_idx: int, included: set[str], excluded: set[str]
    ) -> None:
        """Recursively generate all valid partitions.

        This adds partitions to the valid_partitions list in the outer
        function.

        This algorithm works by going through the base special stars in
        the order prescribed in the outer function. For each base
        special star, we try including it (if possible), including a 100
        coin star alternative of it (if possible), or excluding it (and
        its 100 coin star alternative if it exists). If we choose to
        include a base special star and it has a 100 coin star that can
        replace it, we mark the replacement star as excluded; similarly,
        if we instead include a 100 coin star that replaces a base star,
        we mark the base star as excluded. If we choose to exclude a
        base special star, we ensure that all descendents of that star
        are also excluded.

        Note that we're being careful in this function to ensure that
        each function call gets new copies of the included and excluded
        sets.

        Args:
            star_idx: The index of the ordered_base_special_stars list
              we are currently processing.
            included: A set containing star IDs which are included in
              the partition.
            excluded: A set containing star IDs which are excluded in
              the partition.
        """
        # Base case: processed all special stars. Add the partitions to
        # the valid partitions list.
        if star_idx >= len(ordered_base_special_stars):
            valid_partitions.append((included, excluded))

            return

        # Unpack current star ID
        current_star_id = ordered_base_special_stars[star_idx]

        # If current star is DDD1, ignore it and move to the next
        # prerequisite index: it or it's 100 coin alternative are
        # already included when we started the recursion.
        if current_star_id == DataKeys.STAR_DDD1_ID:
            _generate_valid_partitions_recursive(star_idx + 1, included, excluded)

        # Try including the current base star (and excluding its 100
        # coin star alterative if it exists); and do the other way
        # around.
        for included_star_id, excluded_star_id in _get_star_and_alternative_id_pairs(
            current_star_id, excluded
        ):
            # Add current star to included set
            next_included = included | {included_star_id}

            # Add a possible mutually exclusive star the the excluded
            # set
            next_excluded = excluded.copy()

            if excluded_star_id is not None:
                next_excluded.update({excluded_star_id})

            _generate_valid_partitions_recursive(
                star_idx + 1, next_included, next_excluded
            )

        # Try excluding the current base star and its 100 coin star
        # alternative (if it exists). Also exclude any descendants.
        next_excluded = (
            excluded
            | {current_star_id}
            | find_descendants(
                current_star_id, adjacency_list_dict, base_star_alts_dict
            )
        )

        if current_star_id in base_star_alts_dict:
            next_excluded.update({base_star_alts_dict[current_star_id]})

        _generate_valid_partitions_recursive(
            star_idx + 1, included.copy(), next_excluded
        )

    # Generate and return valid partitions, initializing each partition
    # with either DDD1 or its 100 coin star alternative
    for included_star_id, excluded_star_id in _get_star_and_alternative_id_pairs(
        base_star_id=DataKeys.STAR_DDD1_ID,
        excluded_star_id_set=set(),
    ):
        _generate_valid_partitions_recursive(
            star_idx=0,
            included=set([included_star_id]),
            excluded=set([] if excluded_star_id is None else [excluded_star_id]),
        )

    return valid_partitions
