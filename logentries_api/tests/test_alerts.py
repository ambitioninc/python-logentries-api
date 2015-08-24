from unittest import TestCase

from logentries_api.alerts import (
    PagerDutyAlertConfig, WebHookAlertConfig,
    EmailAlertConfig, SlackAlertConfig,
    HipChatAlertConfig
)


class AlertConfigsTests(TestCase):
    """
    Test each alert type
    """
    def test_pagerduty(self):
        """
        Test PagerDuty schema
        """
        service_key = 'bb7aad43abd9401a9e4f065c9e5ab89f'
        alert = PagerDutyAlertConfig(description='testing', service_key=service_key)

        self.assertDictEqual(
            alert.args(),
            {
                'args': {
                    'description': 'testing',
                    'service_key': 'bb7aad43abd9401a9e4f065c9e5ab89f'
                },
                'type': 'pagerduty'
            }
        )

    def test_email(self):
        """
        Test Email alert
        """
        alert = EmailAlertConfig(address='me@example.com')
        self.assertDictEqual(
            alert.args(),
            {
                'args': {
                    'direct': 'me@example.com',
                    'teams': '',
                    'users': ''
                },
                'type': 'mailto'
            }
        )

    def test_webhook(self):
        """
        Test WebHook schema
        """
        alert = WebHookAlertConfig(url='https://www.google.com')

        self.assertDictEqual(
            alert.args(),
            {
                'args': {
                    'url': 'https://www.google.com'
                },
                'type': 'webhook'
            }
        )

    def test_slack(self):
        """
        Test Slack schema
        """
        alert = SlackAlertConfig(url='https://www.google.com')

        self.assertDictEqual(
            alert.args(),
            {
                'args': {
                    'url': 'https://www.google.com'
                },
                'type': 'slack'
            }
        )

    def test_hipchat(self):
        """
        Test HipChat schema
        """
        token = 'bb7aad43abd9401a9e4f065c9e5ab89f'
        alert = HipChatAlertConfig(token=token, room_name='group')

        self.assertDictEqual(
            alert.args(),
            {
                'args': {
                    'notification_key': token,
                    'room_name': 'group'
                },
                'type': 'hipchat'
            }
        )
