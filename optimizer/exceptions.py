"""Contains exceptions for the program."""


class ConfigFileInvalid(Exception):
    """A config file is invalid."""


class ConfigFileNotFound(Exception):
    """A config file couldn't be found."""


class InvalidExcludedStarIds(Exception):
    """Excluded star IDs make a valid route impossible."""


class NoValidRoutePossible(Exception):
    """No valid route could not be found."""


class InsufficientRemainingStars(Exception):
    """Ran out of remaining non-special stars."""
