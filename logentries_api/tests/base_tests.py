import json
import os
from unittest import TestCase

import requests

from mock import patch, Mock

from logentries_api.base import Resource
from logentries_api.exceptions import ConfigurationException, ServerException


class ResourceTests(TestCase):
    """
    Tests for Resource class
    """

    @patch.object(os.environ, 'get', spec_set=True)
    def test_no_environ_variable(self, os_environ_mock):
        """
        Test a ConfigurationException is raised without the env variable set
        """
        os_environ_mock.return_value = None
        with self.assertRaises(ConfigurationException):
            Resource()

        os_environ_mock.assert_called_once_with('LOGENTRIES_ACCOUNT_KEY')

    @patch.object(requests, 'post')
    def test_post_not_ok(self, mock_post):
        """
        Test ._post() handles a not ok response
        """
        mock_response = Mock(
            name='response',
            ok=False,
            status_code=500,
            text='Server Error'
        )
        mock_post.return_value = mock_response

        resource = Resource(account_key='123')

        with self.assertRaises(ServerException):
            resource._post(request='test1', uri='test_endpoint')

        mock_post.assert_called_once_with(
            url='https://api.logentries.com/v2/test_endpoint',
            headers={'Content-type': 'application/json'},
            data=json.dumps({'acl': '123', 'account': '123', 'request': 'test1'})
        )

    @patch.object(requests, 'post')
    def test_post_ok(self, mock_post):
        """
        Test ._post() handles a response
        """
        mock_response = Mock(
            name='response',
            ok=True,
            status_code=200,
        )
        mock_response.json.return_value = {"status": "ok", "tags": []}
        mock_post.return_value = mock_response

        resource = Resource(account_key='123')

        response = resource._post(request='list', uri='tags')

        self.assertDictEqual(
            response,
            {"status": "ok", "tags": []}
        )

        mock_post.assert_called_once_with(
            url='https://api.logentries.com/v2/tags',
            headers={'Content-type': 'application/json'},
            data=json.dumps({'acl': '123', 'account': '123', 'request': 'list'})
        )
