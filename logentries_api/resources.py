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


def dict_is_subset(d1, d2):
    return all((k in d2 and d2[k] == v) for k, v in d1.items())


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

    def get(self, name):
        """
        Get labels by name

        :param name: The label name, it must be an exact match.
        :type name: str

        :return: A list of matching labels. An empty list is returned if there are
            not any matches
        :rtype: list of dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        labels = self.list()
        return [
            label
            for label
            in labels
            if name == label.get('name')
        ]

    def update(self, label):
        """
        Update a Label

        :param label: The data to update. Must include keys:

            * id (str)
            * appearance (dict)
            * description (str)
            * name (str)
            * title (str)
        :type label: dict

        Example:

        .. code-block:: python

            Labels().update(
                label={
                    'id': 'd9d4596e-49e4-4135-b3b3-847f9e7c1f43',
                    'appearance': {'color': '278abe'},
                    'name': 'My Sandbox',
                    'description': 'My Sandbox',
                    'title': 'My Sandbox',
                }
            )

        :return:
        :rtype: dict
        """
        data = {
            'id': label['id'],
            'name': label['name'],
            'appearance': label['appearance'],
            'description': label['description'],
            'title': label['title'],
        }
        return self._post(
            request=ApiActions.UPDATE.value,
            uri=ApiUri.TAGS.value,
            params=data
        )

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

    def get(self, label_sn):
        """
        Get tags by a label's sn key

        :param label_sn: A corresponding label's ``sn`` key.
        :type label_sn: str or int

        :return: A list of matching tags. An empty list is returned if there are
            not any matches
        :rtype: list of dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        tags = self.list()
        return [
            tag
            for tag
            in tags
            if str(label_sn) in tag.get('args', {}).values()
        ]

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

    def get(self, name_or_tag_id):
        """
        Get hooks by name or tag_id.
        :param name_or_tag_id: The hook's name or associated tag['id']
        :type name_or_tag_id: str

        :return: A list of matching tags. An empty list is returned if there are
            not any matches
        :rtype: list of dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        hooks = self.list()

        return [
            hook
            for hook
            in hooks
            if name_or_tag_id in hook.get('actions')
            or name_or_tag_id == hook.get('name')
        ]

    def update(self, hook):
        """
        Update a hook

        :param hook: The data to update. Must include keys:

            * id (str)
            * name (str)
            * triggers (list of str)
            * sources (list of str)
            * groups (list of str)
            * actions (list of str)
        :type hook: dict

        Example:

        .. code-block:: python

            Hooks().update(
                hook={
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

        :return:
        :rtype: dict
        """
        data = {
            'id': hook['id'],
            'name': hook['name'],
            'triggers': hook['triggers'],
            'sources': hook['sources'],
            'groups': hook['groups'],
            'actions': hook['actions'],
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

    def create(self,
               alert_config,
               occurrence_frequency_count=None,
               occurrence_frequency_unit=None,
               alert_frequency_count=None,
               alert_frequency_unit=None):
        """
        Create a new alert

        :param alert_config: A list of AlertConfig classes (Ex:
            ``[EmailAlert('me@mydomain.com')]``)
        :type alert_config: list of
            :class:`PagerDutyAlert<logentries_api.alerts.PagerDutyAlert>`,
            :class:`WebHookAlert<logentries_api.alerts.WebHookAlert>`,
            :class:`EmailAlert<logentries_api.alerts.EmailAlert>`,
            :class:`SlackAlert<logentries_api.alerts.SlackAlert>`, or
            :class:`HipChatAlert<logentries_api.alerts.HipChatAlert>`

        :param occurrence_frequency_count: How many times per
            ``alert_frequency_unit`` for a match before issuing an alert.
            Defaults to 1
        :type occurrence_frequency_count: int

        :param occurrence_frequency_unit: The time period to monitor for sending
            an alert. Must be 'day', or 'hour'. Defaults to 'hour'
        :type occurrence_frequency_unit: str

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
            'rate_count': occurrence_frequency_count or 1,
            'rate_range': occurrence_frequency_unit or 'hour',
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

    def get(self, alert_type, alert_args=None):
        """
        Get alerts that match the alert type and args.

        :param alert_type: The type of the alert. Must be one of 'pagerduty',
            'mailto', 'webhook', 'slack', or 'hipchat'
        :type alert_type: str

        :param alert_args: The args for the alert. The provided args must be a
            subset of the actual alert args. If no args are provided, all
            alerts matching the ``alert_type`` are returned. For example:
            ``.get('mailto', alert_args={'direct': 'me@mydomain.com'})`` or
            ``.get('slack', {'url': 'https://hooks.slack.com/services...'})``

        :return: A list of matching alerts. An empty list is returned if there
            are not any matches
        :rtype: list of dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        alert_args = alert_args or {}

        alerts = self.list()
        return [
            alert
            for alert
            in alerts
            if alert.get('type') == alert_type
            and dict_is_subset(alert_args, alert.get('args'))
        ]

    def update(self, alert):
        """
        Update an alert

        :param alert: The data to update. Must include keys:

            * id (str)
            * rate_count (int)
            * rate_range (str): 'day' or 'hour'
            * limit_count (int)
            * limit_range (str): 'day' or 'hour'
            * type (str)
            * schedule (list)
            * args (dict)
        :type alert: dict

        Example:

        .. code-block:: python

            Alert().update(
                alert={
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
            )

        :return:
        :rtype: dict
        """
        data = {
            'id': alert['id'],
            'args': alert['args'],
            'rate_count': alert['rate_count'],
            'rate_range': alert['rate_range'],
            'limit_count': alert['limit_count'],
            'limit_range': alert['limit_range'],
            'schedule': alert['schedule'],
            'enabled': alert['enabled'],
            'type': alert['type'],
        }

        return self._post(
            request=ApiActions.UPDATE.value,
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
