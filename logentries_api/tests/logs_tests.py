from unittest import TestCase

import requests
from mock import patch, Mock

from logentries_api.exceptions import ServerException
from logentries_api.logs import LogSets


class LogSetsTests(TestCase):
    """
    Tests for the LogSets class
    """
    def setUp(self):
        super(LogSetsTests, self).setUp()

        self.test_account_key = '4a161599-2634-428c-948f-044e13feac18'
        self.logsets = LogSets(self.test_account_key)

    @patch.object(requests, 'get')
    def test_list_ok(self, mock_get):
        """
        Test .list() is ok
        """
        mock_response = Mock(
            name='response',
            ok=True,
            status_code=200,
        )
        mock_response.json.return_value = {
            'list': [
                {
                    'c': 1438273935310,
                    'distname': 'Ubuntu',
                    'distver': '12.04',
                    'hostname': 'ip-10-10-10-10.ec2.internal',
                    'key': '22613f4d-36f5-489d-88bd-de881c3ec53c',
                    'logs': [{'key': 'fec0027c-7aaa-4dd5-a41c-a62164fa7b54'}],
                    'name': 'ip-10-10-10-10',
                    'object': 'host'
                }, {
                    'c': 1438196071310,
                    'distname': '',
                    'distver': '',
                    'hostname': 'nonlocation',
                    'key': '3e5c020c-82b2-4af3-9cb9-6ce96f4b27e9',
                    'logs': [{'key': '572dfcbf-ff2d-40db-a364-004cf1bb632a'}],
                    'name': 'OtherLogs',
                    'object': 'host'
                }
            ],
            'object': 'hostlist',
            'response': 'ok'
        }
        mock_get.return_value = mock_response

        response = self.logsets.list()

        mock_get.assert_called_once_with(
            self.logsets.base_url
        )
        self.assertEqual(
            response,
            {
                'ip-10-10-10-10': [
                    'fec0027c-7aaa-4dd5-a41c-a62164fa7b54'
                ],
                'OtherLogs': [
                    '572dfcbf-ff2d-40db-a364-004cf1bb632a'
                ]
            }
        )

    @patch.object(requests, 'get')
    def test_list_not_ok(self, mock_get):
        """
        Test .list() fails loudly
        """
        mock_response = Mock(
            name='response',
            ok=False,
            status_code=500,
            text='Server Error'
        )
        mock_get.return_value = mock_response

        with self.assertRaises(ServerException):
            self.logsets.list()

        mock_get.assert_called_once_with(
            self.logsets.base_url
        )

    @patch.object(requests, 'get')
    def test_get_ok(self, mock_get):
        """
        Test .get() is ok
        """

        api_response = {
            'created': 1438276333925,
            'filename': '',
            'follow': 'false',
            'key': '370ec2e9-cf92-491b-881b-0f87e6251901',
            'name': 'nginx',
            'object': 'log',
            'response': 'ok',
            'retention': -1,
            'token': 'f413f087-f860-4377-a78f-2c6877048a01',
            'type': 'token'
        }

        mock_response = Mock(
            name='response',
            ok=True,
            status_code=200,
        )
        mock_response.json.return_value = api_response
        mock_get.return_value = mock_response

        response = self.logsets.get('some_logs/nginx/')

        mock_get.assert_called_once_with(
            self.logsets.base_url + 'some_logs/nginx'
        )
        self.assertEqual(
            response,
            api_response
        )

    @patch.object(requests, 'get')
    def test_get_not_ok(self, mock_get):
        """
        Test .get() fails loudly
        """
        mock_response = Mock(
            name='response',
            ok=False,
            status_code=500,
            text='Server Error'
        )
        mock_get.return_value = mock_response

        with self.assertRaises(ServerException):
            self.logsets.get('some_logs/nginx/')

        mock_get.assert_called_once_with(
            self.logsets.base_url + 'some_logs/nginx'
        )
