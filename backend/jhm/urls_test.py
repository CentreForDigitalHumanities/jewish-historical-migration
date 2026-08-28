from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
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


class ApiAuthLoginTest(TestCase):
    password = 'test-password'

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='api-login-test',
            password=self.password,
        )

    def test_direct_login_redirects_to_api_root(self):
        response = self.client.post('/api-auth/login/', {
            'username': self.user.username,
            'password': self.password,
        })

        self.assertRedirects(response, '/api/')
        self.assertEqual(
            self.client.session['_auth_user_id'],
            str(self.user.pk),
        )

    def test_next_parameter_overrides_default_redirect(self):
        response = self.client.post('/api-auth/login/', {
            'username': self.user.username,
            'password': self.password,
            'next': '/api/records/',
        })

        self.assertRedirects(
            response,
            '/api/records/',
            fetch_redirect_response=False,
        )
