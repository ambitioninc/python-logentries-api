"""
Classes that inherit from ``AlertConfig`` are used to configure Logentries
alerts. Each class has it's own inputs that are specified in the ``__init__``
method.

Each class has a ``.args()`` method that is used properly set the alert
arguments.
"""
from abc import ABCMeta, abstractmethod
from enum import Enum

import six


class AlertTypes(Enum):
    PAGERDUTY = 'pagerduty'
    EMAIL = 'mailto'
    WEBHOOK = 'webhook'
    SLACK = 'slack'
    HIPCHAT = 'hipchat'


class AlertConfig(six.with_metaclass(ABCMeta, object)):
    """
    An abstract class for alerts
    """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @abstractmethod
    def args(self):
        """
        Must return a dictionary with an `args` for the alert, and a `type` key
        with the type
        :rtype: dict
        """
        raise NotImplementedError


class PagerDutyAlertConfig(AlertConfig):
    """
    A PagerDuty AlertConfig configuration
    """
    def __init__(self, description, service_key):
        """
        Requires a 'description' and 'service_key' parameter
        """
        super(PagerDutyAlertConfig, self).__init__(
            description=description,
            service_key=service_key
        )

    def args(self):
        """
        :rtype: dict
        """
        return {
            'args': {
                'service_key': self.service_key,
                'description': self.description,
            },
            'type': AlertTypes.PAGERDUTY.value
        }


class EmailAlertConfig(AlertConfig):
    """
    An email AlertConfig configuration
    """
    def __init__(self, address):
        """
        Requires an 'address' parameter
        """
        super(EmailAlertConfig, self).__init__(address=address)

    def args(self):
        """
        :rtype: dict
        """
        return {
            'args': {
                'direct': self.address,
                'teams': '',
                'users': ''
            },
            'type': AlertTypes.EMAIL.value
        }


class WebHookAlertConfig(AlertConfig):
    """
    A WebHook Alert configuration
    """
    def __init__(self, url):
        """
        Requires a 'url' parameter
        """
        super(WebHookAlertConfig, self).__init__(url=url)

    def args(self):
        """
        :rtype: dict
        """
        return {
            'args': {
                'url': self.url,
            },
            'type': AlertTypes.WEBHOOK.value
        }


class SlackAlertConfig(AlertConfig):
    """
    An Slack Alert configuration
    """
    def __init__(self, url):
        """
        Requires a 'url' parameter
        """
        super(SlackAlertConfig, self).__init__(url=url)

    def args(self):
        """
        :rtype: dict
        """
        return {
            'args': {
                'url': self.url,
            },
            'type': AlertTypes.SLACK.value
        }


class HipChatAlertConfig(AlertConfig):
    """
    An HipChat AlertConfig configuration
    """
    def __init__(self, token, room_name):
        """
        Requires a 'url' parameter
        """
        super(HipChatAlertConfig, self).__init__(
            token=token,
            room_name=room_name
        )

    def args(self):
        """
        :rtype: dict
        """
        return {
            'args': {
                'notification_key': self.token,
                'room_name': self.room_name
            },
            'type': AlertTypes.HIPCHAT.value
        }
