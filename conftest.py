import pytest

@pytest.fixture(autouse=True)
def disable_pagination(settings):
    settings.REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS'] = None