from django.test import TestCase
from django.test.client import RequestFactory
from unittest.mock import MagicMock

import sys
sys.modules['fedireads.outgoing'] = MagicMock()

from fedireads import view_actions, models
from fedireads.connectors.fedireads_connector import Connector
from fedireads.settings import DOMAIN



class ViewActionsTestCase(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.user = models.User.objects.create_user(
            username='cinco', email='cinco@example.com',
            password='five')
        pass

    def test_tag(self):
        request = self.rf.post('/tag/', {
            'name': 'new_tag',
            'book': 42,
        })
        request.user = self.user

        response = view_actions.tag(request)

        sys.modules['fedireads.outgoing'].handle_tag.assert_called_once_with(self.user, 'https://%s/book/42' % (DOMAIN,), 'new_tag')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/book/42')
