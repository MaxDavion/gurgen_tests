# -*- coding: utf-8 -*-
import pytest


@pytest.yield_fixture(scope = "module", autouse = True)
def app(request):
    app_path = request.config.getoption("--path")
    yield app_path


def pytest_addoption(parser):
    parser.addoption("--path", action="store", default='./src/gurgen_0')
    parser.addoption("--run_with_random_tests", action="store_false")


def pytest_runtest_setup(item):
    if 'random_test' in item.keywords and item.config.getvalue("run_with_random_tests") == True:
        pytest.skip("This tests not run in docker")

random_test = pytest.mark.random_test
