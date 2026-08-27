from pathlib import Path
from tempfile import TemporaryDirectory

from django.http import Http404
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve

from .index import index


class BackendOnlyRoutingTest(SimpleTestCase):
    def test_root_redirects_to_admin(self):
        response = self.client.get('/')

        self.assertRedirects(response, '/admin/', fetch_redirect_response=False)

    def test_unknown_path_returns_not_found(self):
        response = self.client.get('/not-a-backend-route')

        self.assertEqual(response.status_code, 404)

    def test_admin_and_api_routes_take_precedence(self):
        self.assertEqual(resolve('/admin/').namespace, 'admin')
        self.assertEqual(resolve('/api/').url_name, 'api-root')


class StaticIndexTest(SimpleTestCase):
    @override_settings(STATICFILES_DIRS=[])
    def test_missing_index_returns_not_found(self):
        request = RequestFactory().get('/')

        with self.assertRaises(Http404):
            index(request)

    def test_index_returns_html_and_sets_csrf_cookie(self):
        with TemporaryDirectory() as static_directory:
            index_path = Path(static_directory) / 'index.html'
            index_path.write_text('<!doctype html><title>Frontend</title>')

            with override_settings(STATICFILES_DIRS=[static_directory]):
                response = index(RequestFactory().get('/'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html')
        self.assertEqual(
            response.content,
            b'<!doctype html><title>Frontend</title>',
        )
        self.assertIn('csrftoken', response.cookies)
