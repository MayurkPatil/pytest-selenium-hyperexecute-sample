import pytest
import os
from os import environ
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.remote_connection import RemoteConnection

@pytest.fixture(scope='function')
def driver(request):

    desired_caps = {}

    browser = {
        # "platform": "MacOS Monterey",
        "platform": "Windows 10",
        "browserName": "chrome",
        "version": "latest"
    }

    desired_caps.update(browser)
    test_name = request.node.name
    build =  "[Python] HyperTest demo using PyTest framework"
    username = os.environ.get("LT_USERNAME")
    access_key = os.environ.get("LT_ACCESS_KEY")

    selenium_endpoint = "https://{}:{}@hub.lambdatest.com/wd/hub".format(username, access_key)
    desired_caps['build'] = build
    desired_caps['name'] = test_name
    desired_caps['video']= True
    desired_caps['visual']= True
    desired_caps['network']= True
    desired_caps['console']= True

    executor = RemoteConnection(selenium_endpoint, resolve_ip=False)
    browser = webdriver.Remote(
        command_executor=executor,
        desired_capabilities=desired_caps
    )
    yield browser

    def fin():
        #browser.execute_script("lambda-status=".format(str(not request.node.rep_call.failed if "passed" else "failed").lower()))
        if request.node.rep_call.failed:
            browser.execute_script("lambda-status=failed")
        else:
            browser.execute_script("lambda-status=passed")
            browser.quit()

    request.addfinalizer(fin)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # this sets the result as a test attribute for LambdaTest reporting.
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)
