''' testing models '''
from django.test import TestCase

from bookwyrm import models
from bookwyrm.settings import DOMAIN


class User(TestCase):
    def setUp(self):
        self.user = models.User.objects.create_user(
            'mouse', 'mouse@mouse.mouse', 'mouseword')

    def test_computed_fields(self):
        ''' username instead of id here '''
        expected_id = 'https://%s/user/mouse' % DOMAIN
        self.assertEqual(self.user.remote_id, expected_id)
        self.assertEqual(self.user.username, 'mouse@%s' % DOMAIN)
        self.assertEqual(self.user.localname, 'mouse')
        self.assertEqual(self.user.shared_inbox, 'https://%s/inbox' % DOMAIN)
        self.assertEqual(self.user.inbox, '%s/inbox' % expected_id)
        self.assertEqual(self.user.outbox, '%s/outbox' % expected_id)
        self.assertIsNotNone(self.user.private_key)
        self.assertIsNotNone(self.user.public_key)


    def test_user_shelves(self):
        shelves = models.Shelf.objects.filter(user=self.user).all()
        self.assertEqual(len(shelves), 3)
        names = [s.name for s in shelves]
        self.assertEqual(names, ['To Read', 'Currently Reading', 'Read'])
        ids = [s.identifier for s in shelves]
        self.assertEqual(ids, ['to-read', 'reading', 'read'])


    def test_activitypub_serialize(self):
        activity = self.user.to_activity()
        self.assertEqual(activity['id'], self.user.remote_id)
        self.assertEqual(activity['@context'], [
            'https://www.w3.org/ns/activitystreams',
            'https://w3id.org/security/v1',
            {
                'manuallyApprovesFollowers': 'as:manuallyApprovesFollowers',
                'schema': 'http://schema.org#',
                'PropertyValue': 'schema:PropertyValue',
                'value': 'schema:value',
            }
        ])
        self.assertEqual(activity['preferredUsername'], self.user.localname)
        self.assertEqual(activity['name'], self.user.name)
        self.assertEqual(activity['inbox'], self.user.inbox)
        self.assertEqual(activity['outbox'], self.user.outbox)
        self.assertEqual(activity['followers'], self.user.ap_followers)
        self.assertEqual(activity['bookwyrmUser'], True)
        self.assertEqual(activity['discoverable'], True)
        self.assertEqual(activity['type'], 'Person')

    def test_activitypub_outbox(self):
        activity = self.user.to_outbox()
        self.assertEqual(activity['type'], 'OrderedCollection')
        self.assertEqual(activity['id'], self.user.outbox)
        self.assertEqual(activity['totalItems'], 0)
