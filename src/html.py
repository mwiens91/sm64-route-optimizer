"""Contains functionality to generate HTML using star data and route data."""

from datetime import datetime
import itertools
from fasthtml import ft
from src.constants import DataKeys, Locations, MAXIMUM_COURSES_PER_ROW
from src import util


def generate_page_html(
    route_star_ids: set[str],
    route_time: float,
    star_times_dict: dict[str, float],
    num_stars_per_location_dict: dict[str, int],
    num_stars_per_course_dict: dict[str, int],
    course_data: list[dict],
) -> str:
    """Build the HTML output page and return it as a string.

    Args:
        route_star_ids: A set containing the star ids used for the
          route.
        route_time: The number of seconds the route takes.
        star_times_dict: A dictionary containing star IDs as keys and
          times as values.
        num_stars_per_location_dict: A dictionary which enumerates the
          number of stars in the route per location.
        num_stars_per_course_dict: A dictionary which enumerates the
          number of stars in the route per course.
        course_data: Course data coming from the course_data module; the
          data should be augmented with the 100 coin stars listed in the
          user config data using functionality in the util module.

    Returns:
        A string containing HTML for the page.
    """
    # Build the summary content for the page
    summary_divs = [
        ft.Div("Route summary:", cls="fw-bold"),
    ]

    # Add the time the route takes
    minutes, remaining_seconds = util.convert_seconds_to_minutes_and_remaining_seconds(
        route_time
    )

    summary_divs.append(
        ft.Div(
            "Sum of star times: "
            + (f"{minutes} minutes " if minutes else "")
            + f"{remaining_seconds:.2f} seconds"
        )
    )

    # Add the number of stars per location
    for location in [
        Locations.LOBBY,
        Locations.COURTYARD,
        Locations.BASEMENT,
        Locations.UPSTAIRS,
        Locations.TIPPY,
    ]:
        summary_divs.append(
            ft.Div(
                location.title()
                + ": "
                + str(num_stars_per_location_dict[location])
                + " stars"
            )
        )

    # Add the time we're making this page
    summary_divs.append(
        ft.Div(
            f"Generated on {datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z%z")}",
            cls="mt-3",
        )
    )

    # For the main content, first build up divs for each course. Filter
    # out courses that do not have stars with times.
    course_divs = []

    for course in sorted(course_data, key=lambda d: d[DataKeys.COURSE_NUMBER]):
        # First build up a table containing the stars for each course
        star_table_rows = []

        for star in sorted(
            course[DataKeys.COURSE_STARS], key=lambda d: d[DataKeys.STAR_NUMBER]
        ):
            if (star_id := star[DataKeys.STAR_ID]) in star_times_dict:
                star_table_rows.append(
                    ft.Tr(
                        ft.Td(
                            ("✓" if star_id in route_star_ids else ""),
                        ),
                        ft.Td(star[DataKeys.STAR_NUMBER]),
                        ft.Td(star[DataKeys.STAR_NAME]),
                        ft.Td(f"{star_times_dict[star_id]:.1f}", cls="text-end"),
                    )
                )

        # If there are any stars in the course, make a div for the
        # course
        if star_table_rows:
            course_divs.append(
                ft.Div(
                    ft.H4(
                        ft.Span(
                            course[DataKeys.COURSE_NAME],
                            cls="badge text-bg-secondary",
                        ),
                        ft.Span(
                            f"{num_stars_per_course_dict[course[DataKeys.COURSE_ID]]} stars",
                            cls="badge rounded-pill text-bg-secondary",
                        ),
                        cls="d-flex justify-content-between align-items-center w-100",
                    ),
                    ft.Table(
                        ft.Colgroup(
                            ft.Col(),
                            ft.Col(width="6%"),
                            ft.Col(width="100%"),
                            ft.Col(),
                        ),
                        ft.Tbody(*star_table_rows),
                        cls="table",
                    ),
                    cls="col",
                )
            )

    # Now put the courses in rows
    course_row_divs = []

    # We have the same iterator being passed MAXIMUM_COURSES_PER_ROW
    # times to a zip function, which will yield us course divs in groups
    # of MAXIMUM_COURSES_PER_ROW
    for course_div_group in itertools.zip_longest(
        *([iter(course_divs)] * MAXIMUM_COURSES_PER_ROW)
    ):
        course_row_divs.append(
            ft.Div(
                *[
                    course_div if course_div is not None else ft.Div(cls="col")
                    for course_div in course_div_group
                ],
                cls="row py-3",
            )
        )

    # Make the page
    page = ft.Html(
        ft.Head(
            ft.Meta(charset="utf-8"),
            ft.Meta(name="viewport", content="width=device-width, initial-scale=1"),
            ft.Title("Super Mario 64 Route Optimizer"),
            # Bootstrap
            ft.Link(
                href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
                rel="stylesheet",
                integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH",
                crossorigin="anonymous",
            ),
            ft.Script(
                src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
                integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz",
                crossorigin="anonymous",
            ),
        ),
        ft.Body(
            ft.Div(
                ft.Div(
                    ft.H1(
                        "Super Mario 64 Route Optimizer",
                        cls="display-3",
                    ),
                    cls="bg-primary-subtle text-primary-emphasis rounded px-3 py-4 my-3",
                ),
                ft.Div(
                    *summary_divs,
                    cls="bg-secondary-subtle text-secondary-emphasis rounded px-3 py-3",
                ),
                ft.Div(
                    *course_row_divs,
                    cls="mt-3 px-1",
                ),
                cls="container",
            )
        ),
        lang="en",
    )

    # Add a doctype tag and then return the HTML
    # NOTE: this is not particularly beautiful code. My understanding is
    # FastHTML is not really designed to for generating static HTML like
    # I'm doing here.
    return "<!DOCTYPE html>\n" + ft.to_xml(page)
