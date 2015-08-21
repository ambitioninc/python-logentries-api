from unittest import TestCase

from mock import patch

from logentries_api.resources import (
    random_color, dict_is_subset,
    Labels, Tags, Hooks, Alerts
)
from logentries_api.alerts import WebHookAlert


class ColorTests(TestCase):
    """
    Tests color stuff
    """

    def test_random_color(self):
        some_color = random_color()
        self.assertRegexpMatches(some_color, r'[A-F0-9]{6}')


class SupportTests(TestCase):
    """
    Tests for other functions
    """

    def test_dict_is_subset_true(self):
        d1 = {'a': 'a'}
        d2 = {'a': 'a', 'b': 'b'}

        self.assertTrue(dict_is_subset({}, d1))
        self.assertTrue(dict_is_subset(d1, d2))

    def test_dict_is_subset_false(self):

        d1 = {'a': 'a'}
        d2 = {'a': 'a', 'b': 'b'}

        self.assertFalse(dict_is_subset(d1, {}))
        self.assertFalse(dict_is_subset(d2, d1))


class LabelsTests(TestCase):
    """
    Tests for the Labels class
    """
    def setUp(self):
        super(LabelsTests, self).setUp()
        self.label = Labels('123')

    @patch.object(Labels, '_post')
    def test_create(self, mock_post):
        """
        Test .create()
        """
        self.label.create('newlabel', color='888888')
        mock_post.assert_called_once_with(
            request='create',
            uri='tags',
            params={
                'name': 'newlabel',
                'title': 'newlabel',
                'description': 'newlabel',
                'appearance': {
                    'color': '888888'
                }
            }
        )

    @patch.object(Labels, '_post')
    def test_list(self, mock_post):
        """
        Test .list()
        """
        self.label.list()
        mock_post.assert_called_once_with(
            request='list',
            uri='tags',
        )

    @patch.object(Labels, 'list')
    def test_get(self, mock_list):
        """
        Test .get()
        """
        mock_list.return_value = [
            {
                'name': 'abcd'
            }, {
                'name': 'label1'
            }
        ]
        response = self.label.get('label1')

        self.assertEqual(
            response,
            [{'name': 'label1'}]
        )

    @patch.object(Labels, 'list')
    def test_get_none(self, mock_list):
        """
        Test .get() with no matches
        """
        mock_list.return_value = [
            {
                'name': 'abcd'
            }, {
                'name': 'label1'
            }
        ]
        response = self.label.get('other')

        self.assertEqual(response, [])

    @patch.object(Labels, '_post')
    def test_update(self, mock_post):
        """
        Test .update()
        """
        label = {
            'should not get through': 'nope',
            'id': 'd9d4596e-49e4-4135-b3b3-847f9e7c1f43',
            'name': 'My Sandbox',
            'description': 'My Sandbox',
            'title': 'My Sandbox',
            'appearance': {
                'color': '888888'
            },
        }

        self.label.update(label)

        mock_post.assert_called_once_with(
            request='update',
            uri='tags',
            params={
                'id': 'd9d4596e-49e4-4135-b3b3-847f9e7c1f43',
                'name': 'My Sandbox',
                'description': 'My Sandbox',
                'title': 'My Sandbox',
                'appearance': {
                    'color': '888888'
                },
            }
        )

    @patch.object(Labels, '_post')
    def test_delete(self, mock_post):
        """
        Test .delete()
        """
        self.label.delete('006d95a8-4fac-42c4-90ed-c3c34978de3e')
        mock_post.assert_called_once_with(
            request='delete',
            uri='tags',
            params={'id': '006d95a8-4fac-42c4-90ed-c3c34978de3e'}
        )


class TagsTests(TestCase):
    """
    Tests for the Tags class
    """
    def setUp(self):
        super(TagsTests, self).setUp()
        self.tags = Tags('123')

    @patch.object(Tags, '_post')
    def test_create(self, mock_post):
        """
        Test .create()
        """
        self.tags.create('1000')
        mock_post.assert_called_once_with(
            request='create',
            uri='actions',
            params={
                'type': 'tagit',
                'rate_count': 0,
                'rate_range': 'day',
                'limit_count': 0,
                'limit_range': 'day',
                'schedule': [],
                'enabled': True,
                'args': {
                    'sn': '1000',
                    'tag_sn': '1000'
                }
            }
        )

    @patch.object(Tags, '_post')
    def test_list(self, mock_post):
        """
        Test .list()
        """
        self.tags.list()
        mock_post.assert_called_once_with(
            request='list',
            uri='actions',
        )

    @patch.object(Tags, 'list')
    def test_get(self, mock_list):
        """
        Test .get()
        """
        mock_list.return_value = [
            {
                'args': {'sn': '1111'}
            }, {
                'args': {'sn': '2222'}
            }
        ]
        response = self.tags.get('1111')

        self.assertEqual(
            response,
            [{'args': {'sn': '1111'}}]
        )

    @patch.object(Tags, 'list')
    def test_get_none(self, mock_list):
        """
        Test .get() with no matches
        """
        mock_list.return_value = [
            {
                'args': {'sn': '1111'}
            }, {
                'args': {'sn': '2222'}
            }
        ]
        response = self.tags.get('3333')

        self.assertEqual(response, [])

    @patch.object(Tags, '_post')
    def test_delete(self, mock_post):
        """
        Test .delete()
        """
        self.tags.delete('006d95a8-4fac-42c4-90ed-c3c34978de3e')
        mock_post.assert_called_once_with(
            request='delete',
            uri='actions',
            params={'id': '006d95a8-4fac-42c4-90ed-c3c34978de3e'}
        )


class HooksTests(TestCase):
    """
    Tests for the Hooks class
    """
    def setUp(self):
        super(HooksTests, self).setUp()
        self.hooks = Hooks('123')

        self.hook_dict = {
            'actions': ['35c73af7-d72b-45e7-a1af-94d1a66383f7'],
            'groups': [],
            'id': '6e39eeb3-c5ba-48c3-95bb-3692d6ef4d22',
            'name': 'curl user_agent',
            'sources': ['580a199c-8e25-4f60-9369-16390fd047e0'],
            'triggers': ['user_agent = /curl\\/[\\d.]*/']
        }

    @patch.object(Hooks, '_post')
    def test_create(self, mock_post):
        """
        Test .create()
        """
        self.hooks.create(
            'newhook',
            regexes=['hostname = /*.example.com/'],
            tag_ids=['ce5eb877-a0ea-4a0a-ac38-7b7e83a1c307'],
            logs=['0a4cb373-0ab5-4934-ab99-b6236c7324ff']
        )
        mock_post.assert_called_once_with(
            request='create',
            uri='hooks',
            params={
                'name': 'newhook',
                'triggers': ['hostname = /*.example.com/'],
                'sources': ['0a4cb373-0ab5-4934-ab99-b6236c7324ff'],
                'groups': [],
                'actions': [
                    'ce5eb877-a0ea-4a0a-ac38-7b7e83a1c307'
                ],
            }
        )

    @patch.object(Hooks, '_post')
    def test_list(self, mock_post):
        """
        Test .list()
        """
        self.hooks.list()
        mock_post.assert_called_once_with(
            request='list',
            uri='hooks',
        )

    @patch.object(Hooks, 'list')
    def test_get(self, mock_list):
        """
        Test .get()
        """
        mock_list.return_value = [
            {
                'name': 'abcd',
                'actions': [],
            }, {
                'name': 'hook1',
                'actions': [],
            }
        ]
        response = self.hooks.get('hook1')

        self.assertEqual(
            response,
            [{'name': 'hook1', 'actions': []}]
        )

    @patch.object(Hooks, 'list')
    def test_get_none(self, mock_list):
        """
        Test .get() with no matches
        """
        mock_list.return_value = [
            {
                'name': 'abcd',
                'actions': [],
            }, {
                'name': 'hook1',
                'actions': [],
            }
        ]
        response = self.hooks.get('hook2')

        self.assertEqual(response, [])

    @patch.object(Hooks, '_post')
    def test_update(self, mock_post):
        """
        Test .update()
        """
        hook = {
            'should not get through': 'nope',
            'id': 'd9d4596e-49e4-4135-b3b3-847f9e7c1f43',
            'name': 'My Sandbox',
            'triggers': [
                'host = you.example.com'
            ],
            'sources': [
                '4d42c719-4005-4929-aa4a-994da4b95040'
            ],
            'groups': [],
            'actions': [
                '9f6adf69-37b9-4a4b-88fb-c3fc4c781a11',
                'ddc36d71-33cb-4f4f-be1b-8591814b1946'
            ],
        }

        self.hooks.update(hook)

        mock_post.assert_called_once_with(
            request='update',
            uri='hooks',
            params={
                'id': 'd9d4596e-49e4-4135-b3b3-847f9e7c1f43',
                'name': 'My Sandbox',
                'triggers': [
                    'host = you.example.com'
                ],
                'sources': [
                    '4d42c719-4005-4929-aa4a-994da4b95040'
                ],
                'groups': [],
                'actions': [
                    '9f6adf69-37b9-4a4b-88fb-c3fc4c781a11',
                    'ddc36d71-33cb-4f4f-be1b-8591814b1946'
                ],
            }
        )

    @patch.object(Hooks, '_post')
    def test_delete(self, mock_post):
        """
        Test .delete()
        """
        self.hooks.delete('006d95a8-4fac-42c4-90ed-c3c34978de3e')
        mock_post.assert_called_once_with(
            request='delete',
            uri='hooks',
            params={'id': '006d95a8-4fac-42c4-90ed-c3c34978de3e'}
        )


class AlertsTests(TestCase):
    """
    Tests for the Alerts class
    """
    def setUp(self):
        super(AlertsTests, self).setUp()
        self.alerts = Alerts('123')

    @patch.object(Alerts, '_post')
    def test_create(self, mock_post):
        """
        Test .create()
        """
        alert_config = WebHookAlert(url='https://www.google.com')

        self.alerts.create(alert_config)
        mock_post.assert_called_once_with(
            request='create',
            uri='actions',
            params={
                'rate_count': 1,
                'rate_range': 'hour',
                'limit_count': 1,
                'limit_range': 'hour',
                'schedule': [],
                'enabled': True,
                'type': 'webhook',
                'args': {
                    'url': 'https://www.google.com'
                }
            }
        )

    @patch.object(Alerts, '_post')
    def test_list(self, mock_post):
        """
        Test .list()
        """
        self.alerts.list()
        mock_post.assert_called_once_with(
            request='list',
            uri='actions',
        )

    @patch.object(Alerts, 'list')
    def test_get_no_args(self, mock_list):
        """
        Test .get() without alert_args
        """
        mock_list.return_value = [
            {
                'type': 'slack',
                'args': {'url': 'https://hooks.slack.com/services/111'}
            }, {
                'type': 'slack',
                'args': {'url': 'https://hooks.slack.com/services/222'}
            }, {
                'type': 'mailto',
                'args': {'direct': 'you@example.com'}
            }
        ]
        response = self.alerts.get('slack')

        self.assertEqual(
            response,
            [{
                'type': 'slack',
                'args': {'url': 'https://hooks.slack.com/services/111'}
            }, {
                'type': 'slack',
                'args': {'url': 'https://hooks.slack.com/services/222'}
            }]
        )

    @patch.object(Alerts, 'list')
    def test_get_with_args(self, mock_list):
        """
        Test .get() with alert_args
        """
        mock_list.return_value = [
            {
                'type': 'slack',
                'args': {'url': 'https://hooks.slack.com/services/111'}
            }, {
                'type': 'slack',
                'args': {'url': 'https://hooks.slack.com/services/222'}
            }, {
                'type': 'mailto',
                'args': {'direct': 'you@example.com'}
            }
        ]
        response = self.alerts.get('slack', {'url': 'https://hooks.slack.com/services/111'})

        self.assertEqual(
            response,
            [{
                'type': 'slack',
                'args': {'url': 'https://hooks.slack.com/services/111'}
            }]
        )

    @patch.object(Alerts, 'list')
    def test_get_none(self, mock_list):
        """
        Test .get() with no matches
        """
        mock_list.return_value = [
            {
                'type': 'mailto',
                'args': {'direct': 'you@example.com'}
            }
        ]
        response = self.alerts.get('slack')

        self.assertEqual(response, [])

    @patch.object(Alerts, '_post')
    def test_update(self, mock_post):
        """
        Test .update()
        """
        label = {
            'should not get through': 'nope',
            'id': 'd9d4596e-49e4-4135-b3b3-847f9e7c1f43',
            'args': {'direct': 'you@example.com'},
            'rate_count': 1,
            'rate_range': 'hour',
            'limit_count': 1,
            'limit_range': 'hour',
            'schedule': [],
            'enabled': True,
            'type': 'mailto',
        }

        self.alerts.update(label)

        mock_post.assert_called_once_with(
            request='update',
            uri='actions',
            params={
                'id': 'd9d4596e-49e4-4135-b3b3-847f9e7c1f43',
                'args': {'direct': 'you@example.com'},
                'rate_count': 1,
                'rate_range': 'hour',
                'limit_count': 1,
                'limit_range': 'hour',
                'schedule': [],
                'enabled': True,
                'type': 'mailto'
            }
        )

    @patch.object(Alerts, '_post')
    def test_delete(self, mock_post):
        """
        Test .delete()
        """
        self.alerts.delete('006d95a8-4fac-42c4-90ed-c3c34978de3e')
        mock_post.assert_called_once_with(
            request='delete',
            uri='actions',
            params={'id': '006d95a8-4fac-42c4-90ed-c3c34978de3e'}
        )
