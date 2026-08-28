from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import SimpleTestCase, TestCase

from . import __version__


REPOSITORY_URL = (
    'https://github.com/CentreForDigitalHumanities/'
    'jewish-historical-migration'
)
RESEARCH_SOFTWARE_LAB_URL = (
    'https://cdh.uu.nl/about/research-software-lab/'
)


class AdminFooterAssertions:
    def assert_footer(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="admin-footer"')
        self.assertContains(response, 'Jewish Historical Migration')
        self.assertContains(response, 'Source code (BSD 3-Clause License)')
        self.assertContains(response, f'Version {__version__}')
        self.assertContains(response, REPOSITORY_URL)
        self.assertContains(response, RESEARCH_SOFTWARE_LAB_URL)


class AdminFooterStaticFilesTest(SimpleTestCase):
    def test_footer_stylesheet_is_discoverable(self):
        self.assertIsNotNone(finders.find('data/admin_footer.css'))


class AnonymousAdminFooterTest(AdminFooterAssertions, SimpleTestCase):
    def test_footer_is_visible_on_anonymous_login(self):
        self.assert_footer(self.client.get('/admin/login/'))


class AuthenticatedAdminFooterTest(AdminFooterAssertions, TestCase):
    def test_footer_is_visible_on_authenticated_admin(self):
        user = get_user_model().objects.create_user(
            username='admin-footer-test',
            is_staff=True,
        )
        self.client.force_login(user)

        self.assert_footer(self.client.get('/admin/'))
