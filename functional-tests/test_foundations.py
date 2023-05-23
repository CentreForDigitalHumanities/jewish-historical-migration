def test_jewish-historical-migration_frontend(browser, base_address):
    browser.get(base_address)
    assert 'Jewish Historical Migration' in browser.title


def test_jewish-historical-migration_admin(browser, admin_address):
    browser.get(admin_address)
    assert 'Django' in browser.title


def test_jewish-historical-migration_api(browser, api_address):
    browser.get(api_address)
    assert 'Api Root' in browser.title


def test_jewish-historical-migration_api_auth(browser, api_auth_address):
    browser.get(api_auth_address + 'login/')
    assert 'Django REST framework' in browser.title
