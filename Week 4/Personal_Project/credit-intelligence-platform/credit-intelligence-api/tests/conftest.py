from copy import deepcopy

import pytest

from data import BORROWERS, FACILITIES, COVENANTS


ORIGINAL_BORROWERS = deepcopy(BORROWERS)
ORIGINAL_FACILITIES = deepcopy(FACILITIES)
ORIGINAL_COVENANTS = deepcopy(COVENANTS)


@pytest.fixture(autouse=True)
def reset_data():
    """Reset the in-memory data after every test."""

    yield

    BORROWERS.clear()
    BORROWERS.extend(deepcopy(ORIGINAL_BORROWERS))

    FACILITIES.clear()
    FACILITIES.extend(deepcopy(ORIGINAL_FACILITIES))

    COVENANTS.clear()
    COVENANTS.extend(deepcopy(ORIGINAL_COVENANTS))