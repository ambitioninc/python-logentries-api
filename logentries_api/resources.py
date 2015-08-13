"""

To create a new tag called 'user_agent = curl' and associate it with a log called
'someset/somelog',

.. code-block:: python

    from logentries_api import Tags, Hooks, Labels, LogSets

    label = Labels().create('user_agent = curl')
    log = LogSets().get('someset/somelog')
    tag = Tags().create(label['sn'])
    hook = Hooks().create(
        name=label['title'],
        regexes=['user_agent = /curl\/[\d.]*/'],
        tag_id=tag['id'],
        logs=[log['key']]
    )

"""
from copy import copy
from enum import Enum
import random

from logentries_api.base import Resource, ApiActions, ApiUri


class Colors(Enum):
    """
    These are a few preselected hex colors you can use for labels.

    Selected from the Ambition Style Guide
    """
    GREEN = '18ab7e'
    DARK_PURPLE = '374259'
    PURPLE = '554973'
    GRAY = 'b5bdc4'
    BLUE = '278abe'
    YELLOW = 'f9d94f'
    ORANGE = 'f26c36'
    RED = 'e61e56'


def random_color():
    """
    Create a random hex color

    :rtype: str
    """
    r = lambda: random.randint(0, 255)
    color = ('%02X%02X%02X' % (r(), r(), r()))
    return color


class LimitRanges(Enum):
    HOUR = 'hour'
    DAY = 'day'


class RateRanges(Enum):
    HOUR = 'hour'
    DAY = 'day'


class Labels(Resource):
    """
    A class for dealing with labels

    Labels are just text and a color. We'll associate tags with them later
    """

    def create(self, name, description=None, color=None):
        """
        Creates a new label and returns the response

        :param name: The label name
        :type name: str

        :param description: An optional description for the label. The name is
            used if no description is provided.
        :type description: str

        :param color: The hex color for the label (ex: 'ff0000' for red). If no
            color is provided, a random one will be assigned.
        :type color: str

        :returns: The response of your post
        :rtype: dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        data = {
            'name': name,
            'title': name,
            'description': description or name,
            'appearance': {
                'color': color or random_color()
            }
        }
        # Yes, it's confusing. the `/tags/` endpoint is used for labels
        return self._post(
            request=ApiActions.CREATE.value,
            uri=ApiUri.TAGS.value,
            params=data
        )

    def list(self):
        """
        Get all current labels

        :return: The Logentries API response
        :rtype: list of dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        return self._post(
            request='list',
            uri=ApiUri.TAGS.value,
        ).get('tags')

    def delete(self, id):
        """
        Delete the specified label

        :param id: the label's ID
        :type id: str

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        return self._post(
            request=ApiActions.DELETE.value,
            uri=ApiUri.TAGS.value,
            params={'id': id}
        )


class Tags(Resource):
    """
    A class for dealing with tags

    Tags have one or more labels.
    """

    def create(self, label_id):
        """
        Create a new tag

        :param label_id: The Label ID (the 'sn' key of the create label response)
        :type label_id: str

        :returns: The response of your post
        :rtype: dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        data = {
            'type': 'tagit',
            'rate_count': 0,
            'rate_range': 'day',
            'limit_count': 0,
            'limit_range': 'day',
            'schedule': [],
            'enabled': True,
            'args': {
                'sn': label_id,
                'tag_sn': label_id
            }
        }
        # Yes, it's confusing. the `/actions/` endpoint is used for tags, while
        # the /tags/ endpoint is used for labels.
        return self._post(
            request=ApiActions.CREATE.value,
            uri=ApiUri.ACTIONS.value,
            params=data
        )

    def list(self):
        """
        Get all current tags

        :return: All tags
        :rtype: list of dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        return list(
            filter(
                lambda x: x.get('type') == 'tagit',  # pragma: no cover
                self._post(
                    request=ApiActions.LIST.value,
                    uri=ApiUri.ACTIONS.value,
                ).get('actions')
            )
        )

    def delete(self, id):
        """
        Delete the specified tag

        :param id: the tag's ID
        :type id: str

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        return self._post(
            request=ApiActions.DELETE.value,
            uri=ApiUri.ACTIONS.value,
            params={'id': id}
        )


class Hooks(Resource):
    """
    A class for dealing with hooks

    Hooks assign tags based on matching regexes to appropriate logs
    """
    def create(self, name, regexes, tag_ids, logs=None):
        """
        Create a hook

        :param name: The hook's name (should be the same as the tag)
        :type name: str

        :param regexes: The list of regular expressions that Logentries expects.
            Ex: `['user_agent = /curl\/[\d.]*/']` Would match where the
            user-agent is curl.
        :type regexes: list of str

        :param tag_id: The ids of the tags to associate the hook with.
            (The 'id' key of the create tag response)
        :type tag_id: list of str

        :param logs: The logs to add the hook to. Comes from the 'key'
            key in the log dict.
        :type logs: list of str

        :returns: The response of your post
        :rtype: dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        data = {
            'name': name,
            'triggers': regexes,
            'sources': logs or [],
            'groups': [],
            'actions': tag_ids
        }
        return self._post(
            request=ApiActions.CREATE.value,
            uri=ApiUri.HOOKS.value,
            params=data
        )

    def list(self):
        """
        Get all current hooks

        :return: All hooks
        :rtype: list of dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        return self._post(
            request=ApiActions.LIST.value,
            uri=ApiUri.HOOKS.value,
        ).get('hooks')

    def add_hook_to_log(self, hook, log_key):
        """
        Add an existing hook to a specified log

        :param hook: The hook dict
        :type hook: dict

        :param log_key: UUID of the log to be tagged
        :type log_key: str

        :return: The response of your post
        :rtype: dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """

        if log_key not in hook.get('sources', []):
            sources = copy(hook['sources'])
            sources.append(log_key)

            data = {
                'id': hook['id'],
                'name': hook['name'],
                'triggers': hook['triggers'],
                'sources': sources,
                'groups': hook['groups'],
                'actions': hook['actions']
            }
            return self._post(
                request=ApiActions.UPDATE.value,
                uri=ApiUri.HOOKS.value,
                params=data
            )

    def delete(self, id):
        """
        Delete the specified hook

        :param id: the hook's ID
        :type id: str

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        return self._post(
            request=ApiActions.DELETE.value,
            uri=ApiUri.HOOKS.value,
            params={'id': id}
        )


class Alerts(Resource):
    """
    A class for dealing with alerts
    """

    def list(self):
        """
        Get all current alerts

        :return: All alerts
        :rtype: list of dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """

        return list(
            filter(
                lambda x: x.get('type') != 'tagit',  # pragma: no cover
                self._post(
                    request=ApiActions.LIST.value,
                    uri=ApiUri.ACTIONS.value,
                ).get('actions')
            )
        )

    def create(self,
               alert_config,
               alert_frequency_count=None,
               alert_frequency_unit=None):
        """
        Create a new alert

        :param alert_config: A list of AlertConfig classes (Ex:
            [``EmailAlert('me@mydomain.com')``])
        :type alert_config: list of
            :class:`PagerDutyAlert<logentries_api.alerts.PagerDutyAlert>`,
            :class:`WebHookAlert<logentries_api.alerts.WebHookAlert>`,
            :class:`EmailAlert<logentries_api.alerts.EmailAlert>`,
            :class:`SlackAlert<logentries_api.alerts.SlackAlert>`, or
            :class:`HipChatAlert<logentries_api.alerts.HipChatAlert>`

        :param alert_frequency_count: How many times per
            ``alert_frequency_unit`` to issue an alert. Defaults to 1
        :type alert_frequency_count: int

        :param alert_frequency_unit: How often to regulate sending alerts.
            Must be 'day', or 'hour'. Defaults to 'hour'
        :type alert_frequency_unit: str

        :returns: The response of your post
        :rtype: dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        data = {
            'rate_count': 0,
            'rate_range': 'day',
            'limit_count': alert_frequency_count or 1,
            'limit_range': alert_frequency_unit or 'hour',
            'schedule': [],
            'enabled': True,
        }
        data.update(alert_config.args())

        # Yes, it's confusing. the `/actions/` endpoint is used for alerts, while
        # the /tags/ endpoint is used for labels.
        return self._post(
            request=ApiActions.CREATE.value,
            uri=ApiUri.ACTIONS.value,
            params=data
        )

    def delete(self, id):
        """
        Delete the specified alert

        :param id: the alert's ID
        :type id: str

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        return self._post(
            request=ApiActions.DELETE.value,
            uri=ApiUri.ACTIONS.value,
            params={'id': id}
        )
