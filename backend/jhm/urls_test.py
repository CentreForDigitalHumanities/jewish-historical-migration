from django.test import SimpleTestCase
from django.urls import resolve


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
