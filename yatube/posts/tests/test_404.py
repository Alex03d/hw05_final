from django.test import TestCase
from http import HTTPStatus


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        self.assertTemplateUsed(response, 'core/404.html')
