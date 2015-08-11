from enum import Enum
import json

import os
import requests
from logentries_api.exceptions import ConfigurationException, ServerException


class ApiUri(Enum):
    TAGS = 'tags'
    ACTIONS = 'actions'
    HOOKS = 'hooks'


class ApiActions(Enum):
    REGISTER = 'register'
    LIST = 'list'
    CREATE = 'create'
    DELETE = 'delete'
    UPDATE = 'update'


class Resource(object):
    """
    A base class for API resources
    """

    def __init__(self, account_key=None):
        """
        :type account_key: str
        :param account_key: The API key. If no key is passed, the environment
            variable LOGENTRIES_ACCOUNT_KEY is used.
        :raises: If the account_key parameter is not present, and no environment
            variable is present, a
            :class:`ConfigurationException <logentries_api.exceptions.ConfigurationException>`
            is raised.
        """
        self.account_key = account_key or os.environ.get('LOGENTRIES_ACCOUNT_KEY')

        if not self.account_key:
            raise ConfigurationException('LOGENTRIES_ACCOUNT_KEY not present in environment!')

    @property
    def headers(self):
        return {
            'Content-type': 'application/json',
        }

    def _post(self, request, uri, params=None):
        """
        A wrapper for posting things.

        :param request: The request type. Must be one of the
            :class:`ApiActions<logentries_api.base.ApiActions>`
        :type request: str

        :param uri: The API endpoint to hit. Must be one of
            :class:`ApiUri<logentries_api.base.ApiUri>`
        :type uri: str

        :param params: A dictionary of supplemental kw args
        :type params: dict

        :returns: The response of your post
        :rtype: dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        request_data = {
            'acl': self.account_key,
            'account': self.account_key,
            'request': request,
        }

        request_data.update(params or {})

        response = requests.post(
            url='https://api.logentries.com/v2/{}'.format(uri),
            headers=self.headers,
            data=json.dumps(request_data)
        )

        if not response.ok:
            raise ServerException(
                '{}: {}'.format(response.status_code, response.text))
        return response.json()
