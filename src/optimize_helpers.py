"""Contains useful functionality for the optimize module."""

from collections import defaultdict, deque
import functools
import typing


def get_topological_sort_of_prerequisites(
    adjacency_list_dict: dict[str, list[str]]
) -> list[str]:
    """Return a topologically sorted list of prerequisites.

    Topological sorting is done according to Kahn's algorithm.

    Args:
        adjacency_list_dict: A dictionary which has star IDs as keys and
          non-empty lists of star IDs the key star is a prerequisite for
          as values.

    Returns:
        A topologically sorted list of the prerequisites listed in the
        passed in adjacency list dictionary.
    """
    # First, build a dictionary which has star IDs as keys and their
    # in-degrees as values
    in_degree_dict: typing.DefaultDict[str, int] = defaultdict(int)

    for dependants in adjacency_list_dict.values():
        for dependant in dependants:
            in_degree_dict[dependant] += 1

    # Next, we'll maintain a queue which contains star IDs with zero
    # in-degree
    queue = deque(
        prerequisite
        for prerequisite in adjacency_list_dict
        if in_degree_dict[prerequisite] == 0
    )

    # We iteratively pop star IDs from the queue and then (1) remove
    # them from the graph and (2) add them to a stack. Following these
    # operations, any star IDs that now have zero in-degree and are
    # prerequisites are added to the queue. At completion the stack
    # contains a topogical sorting of the prerequisites.
    stack = []

    while queue:
        # Pop prerequisite from queue and add to stack
        prerequisite = queue.pop()

        stack.append(prerequisite)

        # Remove the prerequisite from the graph and add to the queue
        # any prerequisites that now have zero in-degree
        for dependant in adjacency_list_dict[prerequisite]:
            in_degree_dict[dependant] -= 1

            if in_degree_dict[dependant] == 0 and dependant in adjacency_list_dict:
                queue.appendleft(dependant)

    return stack


def find_descendants(
    star_id: str,
    adjacency_list_dict: dict[str, list[str]],
    base_star_alts_dict: dict[str, str],
) -> frozenset[str]:
    """Find all descendants of a given star.

    Args:
        star_id: The ID of the star we're finding descendants for.
        adjacency_list_dict: A dictionary which has non-100 coin star
          IDs as keys and non-empty lists of star IDs the key star is a
          prerequisite for as values.
        base_star_alts_dict: A dictionary with base star IDs as keys and
          100 coin star IDs that can be used to replace the base star as
          values.

    Returns:
        A frozenset containing all prerequisites of the star
    """

    @functools.cache
    def _find_descendants(star_id: str) -> frozenset[str]:
        """Memoized descendant finder.

        Note we could also write this recursively similarly to the
        _find_true_star_count_requirement inner function in the util
        module. It probably would be faster(?).
        """
        descendants = set()
        stack = [star_id]

        while stack:
            current_star_id = stack.pop()

            try:
                for dependant in adjacency_list_dict[current_star_id]:
                    if dependant not in descendants:
                        # Add dependant and its 100 coin star
                        # alternative, if it exists
                        descendants.add(dependant)

                        if dependant in base_star_alts_dict:
                            descendants.add(base_star_alts_dict[dependant])

                        stack.append(dependant)
            except KeyError:
                # Current star not in adjacency list, so has no
                # dependants
                pass

        return frozenset(descendants)

    return _find_descendants(star_id)
