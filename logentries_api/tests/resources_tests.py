from unittest import TestCase

from mock import patch

from logentries_api.resources import (
    random_color,
    Labels, Tags, Hooks, Alerts
)


class ColorTests(TestCase):
    """
    Tests color stuff
    """

    def test_random_color(self):
        some_color = random_color()
        self.assertRegexpMatches(some_color, r'[A-F0-9]{6}')


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
            tag_id='ce5eb877-a0ea-4a0a-ac38-7b7e83a1c307',
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

    @patch.object(Hooks, '_post')
    def test_add_hook_to_log(self, mock_post):
        """
        Test .add_hook_to_log()
        """
        self.hooks.add_hook_to_log(
            hook=self.hook_dict,
            log_key='f5059c57-9425-4668-8552-99626e635e93'
        )

        sources = self.hook_dict.get('sources')
        sources.append('f5059c57-9425-4668-8552-99626e635e93')
        self.hook_dict['sources'] = sources

        mock_post.assert_called_once_with(
            request='update',
            uri='hooks',
            params=self.hook_dict
        )

    @patch.object(Hooks, '_post')
    def test_add_hook_to_log_already_exists(self, mock_post):
        """
        Test .add_hook_to_log()
        """
        sources = self.hook_dict.get('sources')
        sources.append('f5059c57-9425-4668-8552-99626e635e93')
        self.hook_dict['sources'] = sources

        self.hooks.add_hook_to_log(
            hook=self.hook_dict,
            log_key='f5059c57-9425-4668-8552-99626e635e93'
        )
        self.assertFalse(mock_post.called)


class AlertsTests(TestCase):
    """
    Tests for the Alerts class
    """
    def setUp(self):
        super(AlertsTests, self).setUp()
        self.alerts = Alerts('123')

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
