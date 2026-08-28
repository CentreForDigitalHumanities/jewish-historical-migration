def test_root_redirects_to_admin(browser, base_address):
    browser.get(base_address)
    assert browser.current_url == base_address + 'admin/login/?next=/admin/'
    assert 'Django' in browser.title


def test_admin(browser, admin_address):
    browser.get(admin_address)
    assert 'Django' in browser.title


def test_api(browser, api_address):
    browser.get(api_address)
    assert 'Api Root' in browser.title


def test_api_auth(browser, api_auth_address):
    browser.get(api_auth_address + 'login/')
    assert 'Django REST framework' in browser.title
