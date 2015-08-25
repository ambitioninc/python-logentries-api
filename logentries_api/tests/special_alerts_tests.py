import json
from unittest import TestCase

from mock import patch, Mock, call
import requests

from logentries_api.alerts import SlackAlertConfig
from logentries_api.exceptions import ConfigurationException, ServerException
from logentries_api.special_alerts import (
    AlertReportConfig, AlertTriggerConfig,
    SpecialAlertBase, AnomalyAlert, InactivityAlert
)


class AlertReportConfigTests(TestCase):
    """
    Test AlertReportConfig
    """
    def setUp(self):
        self.slack_url = 'https://hooks.slack.com/services'
        self.alert_config = SlackAlertConfig(self.slack_url)

    def test_init_success(self):
        """
        Test __init__ that works
        """
        AlertReportConfig(
            report_count=4,
            report_period='day',
            alert_config=self.alert_config,
        )

    def test_init_fail_report_count(self):
        """
        Test __init__ that has invalid count
        """
        with self.assertRaises(ConfigurationException):
            AlertReportConfig(
                report_count=400,
                report_period='day',
                alert_config=self.alert_config,
            )

    def test_init_fail_report_period(self):
        """
        Test __init__ that has invalid period
        """
        with self.assertRaises(ConfigurationException):
            AlertReportConfig(
                report_count=4,
                report_period='week',
                alert_config=self.alert_config,
            )

    def test_to_dict(self):
        """
        test .to_dict()
        """
        report_config = AlertReportConfig(
            report_count=4,
            report_period='day',
            alert_config=self.alert_config,
        )

        response = report_config.to_dict()

        self.assertDictEqual(
            response,
            {
                'min_report_count': 4,
                'min_report_period': 'Day',
                'type': 'Alert',
                'enabled': True,
                'targets': [
                    {
                        'params_set': {
                            'url': self.slack_url
                        },
                        'type': 'slack'
                    }
                ]
            }
        )


class AlertTriggerConfigTests(TestCase):
    """
    Test AlertTriggerConfig
    """

    def test_init_success(self):
        """
        Test __init__ that works
        """
        AlertTriggerConfig(
            timeframe_value=10,
            timeframe_period='day',
        )

    def test_init_fail_report_count(self):
        """
        Test __init__ that has invalid value
        """
        with self.assertRaises(ConfigurationException):
            AlertTriggerConfig(
                timeframe_value=101,
                timeframe_period='day',
            )

    def test_init_fail_report_period(self):
        """
        Test __init__ that has invalid period
        """
        with self.assertRaises(ConfigurationException):
            AlertTriggerConfig(
                timeframe_value=10,
                timeframe_period='month',
            )

    def test_to_dict(self):
        """
        test .to_dict()
        """
        trigger_config = AlertTriggerConfig(
            timeframe_value=10,
            timeframe_period='day',
        )
        response = trigger_config.to_dict()

        self.assertDictEqual(
            response,
            {
                'timeframe_period': 'Day',
                'timeframe_value': 10,
            }
        )


class SpecialAlertBaseTests(TestCase):
    """
    Test SpecialAlertBase class
    """

    def setUp(self):

        self.username = 'you@example.com'
        self.password = 'password'

        self.account_id = '30c586e0'

        self.csrf_token = '39391011f8864144b7bfb73fca2cd510'

    @patch.object(SpecialAlertBase, '_login')
    def test_init(self, mock_login):
        """
        Test the __init__ method
        """
        mock_login.return_value = self.account_id

        special_alert = SpecialAlertBase(self.username, self.password)

        self.assertEqual(
            special_alert.account_id,
            self.account_id
        )
        mock_login.assert_called_once_with(
            self.username, self.password
        )

    @patch.object(SpecialAlertBase, '_get_csrf_token')
    @patch.object(SpecialAlertBase, '_login')
    def test_get_login_payload(self, mock_login, mock_get_token):
        """
        Test ._get_login_payload() is formatted correctly
        """
        mock_login.return_value = self.account_id
        mock_get_token.return_value = self.csrf_token

        response = SpecialAlertBase(self.username, self.password)._get_login_payload(
            self.username,
            self.password,
        )

        self.assertDictEqual(
            response,
            {
                'csrfmiddlewaretoken': self.csrf_token,
                'ajax': '1',
                'next': '/app/',
                'username': self.username,
                'password': self.password,
            }
        )

    @patch('requests.session', autospec=True)
    @patch.object(SpecialAlertBase, '_login')
    def test_get_csrf_token(self, mock_login, mock_session):
        """
        Test ._get_csrf_token()
        """
        mock_login.return_value = self.account_id

        mock_session.return_value.cookies.get_dict.return_value = {
            'csrftoken': self.csrf_token
        }

        response = SpecialAlertBase(self.username, self.password)._get_csrf_token()

        self.assertEqual(
            response,
            self.csrf_token
        )

    @patch.object(SpecialAlertBase, '_get_csrf_token')
    @patch.object(SpecialAlertBase, '_login')
    def test_get_api_headers(self, mock_login, mock_get_token):
        """
        Test .get_api_headers()
        """
        mock_login.return_value = self.account_id
        mock_get_token.return_value = self.csrf_token

        alert = SpecialAlertBase(self.username, self.password)

        self.assertDictEqual(
            alert._get_api_headers(**{'xxx': 'yyy'}),
            {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json;charset=utf-8',
                'Host': 'logentries.com',
                'Pragma': 'no-cache',
                'Referer': 'https://logentries.com/app/{account_id}'.format(account_id=self.account_id),
                'X-CSRFToken': self.csrf_token,
                'xxx': 'yyy'
            }
        )
        mock_get_token.assert_called_once_with()

    @patch.object(SpecialAlertBase, '_get_api_headers')
    @patch.object(requests.Session, 'post', autospec=True)
    @patch.object(SpecialAlertBase, '_login')
    def test_api_post(self, mock_login, mock_post, mock_headers):
        """
        Test ._api_post()
        """
        mock_login.return_value = self.account_id
        mock_headers.return_value = {}

        url = 'https://logentries.com/app/{account_id}/rest/tag'.format(account_id=self.account_id)

        alert = SpecialAlertBase(self.username, self.password)

        alert._api_post(
            url=url,
            data={'k': 'v'}
        )

        mock_post.assert_called_once_with(
            alert.session,
            url=url,
            headers={},
            data={'k': 'v'}
        )

    @patch.object(SpecialAlertBase, '_get_api_headers')
    @patch.object(requests.Session, 'delete', autospec=True)
    @patch.object(SpecialAlertBase, '_login')
    def test_api_delete(self, mock_login, mock_delete, mock_headers):
        """
        Test ._api_delete()
        """
        mock_login.return_value = self.account_id
        mock_headers.return_value = {}

        url = 'https://logentries.com/app/{account_id}/rest/tag'.format(account_id=self.account_id)

        alert = SpecialAlertBase(self.username, self.password)

        alert._api_delete(
            url=url,
            data={'k': 'v'}
        )

        mock_delete.assert_called_once_with(
            alert.session,
            url=url,
            headers={},
            data={'k': 'v'}
        )

    @patch.object(requests.Session, 'get', autospec=True)
    def test_login_fail_fast(self, mock_get):
        """
        Test the login with a failure on the first get
        """
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_response.ok = False

        mock_get.return_value = mock_response

        session = requests.session()

        with self.assertRaises(ServerException):
            SpecialAlertBase(self.username, self.password, session)

        mock_get.assert_called_once_with(
            session,
            url='https://logentries.com/login/',
            headers=SpecialAlertBase.default_headers
        )

    @patch.object(requests.Session, 'post', autospec=True)
    @patch.object(requests.Session, 'get', autospec=True)
    def test_login_fail_login(self, mock_get, mock_post):
        """
        Test the login with a failure on the post
        """
        mock_get.return_value = Mock()

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_response.ok = False

        mock_post.return_value = mock_response

        session = requests.session()
        session.cookies.set('csrftoken', self.csrf_token)

        with self.assertRaises(ServerException):
            SpecialAlertBase(self.username, self.password, session)

        self.assertEqual(mock_get.call_count, 1)

        headers = SpecialAlertBase.default_headers.copy()
        headers.update({
            'Referer': 'https://logentries.com/login/',
            'X-Requested-With': 'XMLHttpRequest',
        })

        mock_post.assert_called_once_with(
            session,
            'https://logentries.com/login/ajax/',
            headers=headers,
            data={
                'csrfmiddlewaretoken': self.csrf_token,
                'ajax': '1',
                'next': '/app/',
                'username': self.username,
                'password': self.password
            }
        )

    @patch.object(requests.Session, 'post', autospec=True)
    @patch.object(requests.Session, 'get', autospec=True)
    def test_login_fail_app(self, mock_get, mock_post):
        """
        Test the login with a failure on the getting the /app/ page
        """
        mock_get.side_effect = iter([
            Mock(),
            Mock(url='https://logentries.com/app/{account_id}'.format(account_id=self.account_id)),
        ])

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_response.ok = True

        mock_post.return_value = mock_response

        session = requests.session()
        session.cookies.set('csrftoken', self.csrf_token)

        alert = SpecialAlertBase(self.username, self.password, session)

        self.assertEqual(mock_get.call_count, 2)

        headers = SpecialAlertBase.default_headers.copy()
        headers.update({
            'Referer': 'https://logentries.com/login/',
            'X-Requested-With': 'XMLHttpRequest',
        })

        mock_post.assert_called_once_with(
            session,
            'https://logentries.com/login/ajax/',
            headers=headers,
            data={
                'csrfmiddlewaretoken': self.csrf_token,
                'ajax': '1',
                'next': '/app/',
                'username': self.username,
                'password': self.password
            }
        )

        self.assertEqual(
            alert.account_id,
            self.account_id
        )


class InactivityAlertTests(TestCase):
    """
    Test the InactivityAlert class
    """

    def setUp(self):
        self.username = 'you@example.com'
        self.password = 'password'

        self.account_id = '30c586e0'

    @patch.object(requests.Session, 'post', autospec=True)
    @patch.object(SpecialAlertBase, '_login')
    def test_create_fail(self, mock_login, mock_post):
        """
        Test .create() has a failure
        """
        # simulate login
        mock_login.return_value = self.account_id

        # Create the response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Bad Input"
        mock_response.ok = False

        mock_post.return_value = mock_response

        session = requests.session()

        alert = InactivityAlert(self.username, self.password, session)

        name = 'No Successful Web Activity'
        patterns = ['status=200']
        logs = [
            '5d481b23-9c4d-4250-bfe8-be389a227f0b',
            'e0b6b2c0-a4b8-44c4-b57c-25a7f161faf1'
        ]
        trigger_config = AlertTriggerConfig(
            timeframe_value=6,
            timeframe_period='day',
        )
        slack_url = 'https://hooks.slack.com/services'
        alert_config = SlackAlertConfig(slack_url)

        alert_reports = [
            AlertReportConfig(
                report_count=4,
                report_period='day',
                alert_config=alert_config,
            )
        ]
        with self.assertRaises(ServerException):
            alert.create(
                name=name,
                patterns=patterns,
                logs=logs,
                trigger_config=trigger_config,
                alert_reports=alert_reports
            )

        headers = alert.default_headers.copy()
        headers.update({
            'Content-Type': 'application/json;charset=utf-8',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://logentries.com/app/{account_id}'.format(account_id=alert.account_id),
            'X-CSRFToken': alert._get_csrf_token(),
        })

        data = {
            'tag': {
                'actions': [
                    {
                        'enabled': True,
                        'min_report_count': 4,
                        'min_report_period': 'Day',
                        'targets': [{
                            'type': 'slack',
                            'params_set': {
                                'url': slack_url
                            }
                        }],
                        'type': 'Alert',
                    },
                ],
                'name': name,
                'patterns': patterns,
                'sources': [
                    {'id': '5d481b23-9c4d-4250-bfe8-be389a227f0b'},
                    {'id': 'e0b6b2c0-a4b8-44c4-b57c-25a7f161faf1'},
                ],
                'sub_type': 'InactivityAlert',
                'type': 'AlertNotify',
                'timeframe_period': 'Day',
                'timeframe_value': 6

            }
        }

        mock_post.assert_called_once_with(
            session,
            url=alert.url_template.format(account_id=alert.account_id),
            headers=headers,
            data=json.dumps(data, sort_keys=True)
        )

    @patch.object(requests.Session, 'post', autospec=True)
    @patch.object(SpecialAlertBase, '_login')
    def test_create_success(self, mock_login, mock_post):
        """
        Test .create() has a failure
        """
        # simulate login
        mock_login.return_value = self.account_id

        # Create the response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {}
        mock_response.ok = True

        mock_post.return_value = mock_response

        session = requests.session()

        alert = InactivityAlert(self.username, self.password, session)

        # Create the call args
        name = 'No Successful Web Activity'
        patterns = ['status=200']
        logs = [
            '5d481b23-9c4d-4250-bfe8-be389a227f0b',
            'e0b6b2c0-a4b8-44c4-b57c-25a7f161faf1'
        ]
        trigger_config = AlertTriggerConfig(
            timeframe_value=6,
            timeframe_period='day',
        )
        slack_url = 'https://hooks.slack.com/services'
        alert_config = SlackAlertConfig(slack_url)

        alert_reports = [
            AlertReportConfig(
                report_count=4,
                report_period='day',
                alert_config=alert_config,
            )
        ]

        # Call .create()
        alert.create(
            name=name,
            patterns=patterns,
            logs=logs,
            trigger_config=trigger_config,
            alert_reports=alert_reports
        )

        headers = alert.default_headers.copy()
        headers.update({
            'Content-Type': 'application/json;charset=utf-8',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://logentries.com/app/{account_id}'.format(account_id=alert.account_id),
            'X-CSRFToken': alert._get_csrf_token(),
        })

        data = {
            'tag': {
                'actions': [
                    {
                        'enabled': True,
                        'min_report_count': 4,
                        'min_report_period': 'Day',
                        'targets': [{
                            'type': 'slack',
                            'params_set': {
                                'url': slack_url
                            }
                        }],
                        'type': 'Alert',
                    },
                ],
                'name': name,
                'patterns': patterns,
                'sources': [
                    {'id': '5d481b23-9c4d-4250-bfe8-be389a227f0b'},
                    {'id': 'e0b6b2c0-a4b8-44c4-b57c-25a7f161faf1'},
                ],
                'sub_type': 'InactivityAlert',
                'type': 'AlertNotify',
                'timeframe_period': 'Day',
                'timeframe_value': 6

            }
        }

        mock_post.assert_called_once_with(
            session,
            url=alert.url_template.format(account_id=alert.account_id),
            headers=headers,
            data=json.dumps(data, sort_keys=True)
        )

        mock_response.json.assert_called_once_with()

    @patch.object(InactivityAlert, '_api_delete')
    @patch.object(InactivityAlert, '_login')
    def test_delete_fails(self, mock_login, mock_delete):
        """
        Test .delete() has a failure
        """
        mock_login.return_value = self.account_id

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Bad Input"
        mock_response.ok = False

        mock_delete.return_value = mock_response

        alert = InactivityAlert(self.username, self.password)

        with self.assertRaises(ServerException):
            alert.delete('19dede15-118b-467f-bfe9-e9c771d7cc2c')

        mock_delete.assert_called_once_with(
            url='https://logentries.com/rest/{account_id}/api/tags/{tag}'.format(
                account_id=self.account_id,
                tag='19dede15-118b-467f-bfe9-e9c771d7cc2c'
            )
        )

    @patch.object(SpecialAlertBase, '_api_delete')
    @patch.object(SpecialAlertBase, '_login')
    def test_delete_passes(self, mock_login, mock_delete):
        """
        Test .delete() has a failure
        """
        mock_login.return_value = self.account_id

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.ok = True

        mock_delete.return_value = mock_response

        alert = InactivityAlert(self.username, self.password)

        alert.delete('19dede15-118b-467f-bfe9-e9c771d7cc2c')

        mock_delete.assert_called_once_with(
            url='https://logentries.com/rest/{account_id}/api/tags/{tag}'.format(
                account_id=self.account_id,
                tag='19dede15-118b-467f-bfe9-e9c771d7cc2c'
            )
        )


class AnomalyAlertTests(TestCase):
    """
    Test the AnomalyAlert class
    """

    def setUp(self):
        self.username = 'you@example.com'
        self.password = 'password'
        self.account_id = '30c586e0'

    @patch.object(requests.Session, 'post', autospec=True)
    @patch.object(SpecialAlertBase, '_login')
    def test_create_scheduled_query_fail(self, mock_login, mock_post):
        """
        Test ._create_scheduled_query() has a failure
        """
        # simulate login
        mock_login.return_value = self.account_id

        # Create the response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Bad Input"
        mock_response.ok = False

        mock_post.return_value = mock_response

        session = requests.session()

        alert = AnomalyAlert(self.username, self.password, session)

        query = 'where(status=404) calculate(COUNT)'
        scope_count = 1
        scope_unit = 'day'
        change = '+15'

        # Call .create
        with self.assertRaises(ServerException):
            alert._create_scheduled_query(
                query=query,
                change=change,
                scope_count=scope_count,
                scope_unit=scope_unit,
            )

    @patch.object(requests.Session, 'post', autospec=True)
    @patch.object(SpecialAlertBase, '_login')
    def test_create_scheduled_query_pass(self, mock_login, mock_post):
        """
        Test ._create_scheduled_query() passes
        """
        # simulate login
        mock_login.return_value = self.account_id

        # Create the response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'scheduled_query': {
                'id': '00000000-0000-03a2-0000-000000000000'
            }
        }
        mock_response.ok = True

        mock_post.return_value = mock_response

        session = requests.session()

        alert = AnomalyAlert(self.username, self.password, session)

        query = 'where(status=404) calculate(COUNT)'
        scope_count = 1
        scope_unit = 'day'
        change = '+15'

        # Call .create
        response = alert._create_scheduled_query(
            query=query,
            change=change,
            scope_count=scope_count,
            scope_unit=scope_unit,
        )

        self.assertDictEqual(
            response,
            {
                'scheduled_query': {
                    'id': '00000000-0000-03a2-0000-000000000000'
                }
            }
        )

    @patch.object(requests.Session, 'post', autospec=True)
    @patch.object(AnomalyAlert, '_create_scheduled_query')
    @patch.object(SpecialAlertBase, '_login')
    def test_create_fail_post(self, mock_login, mock_scheduled_query, mock_post):
        """
        Test .create() has a failure
        """
        # simulate login
        mock_login.return_value = self.account_id

        mock_scheduled_query.return_value = {
            'scheduled_query': {
                'id': '00000000-0000-03a2-0000-000000000000'
            }
        }

        # Create the response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Bad Input"
        mock_response.ok = False

        mock_post.return_value = mock_response

        session = requests.session()

        alert = AnomalyAlert(self.username, self.password, session)

        name = 'Too many 404s'
        query = 'where(status=404) calculate(COUNT)'
        logs = [
            '5d481b23-9c4d-4250-bfe8-be389a227f0b',
        ]
        trigger_config = AlertTriggerConfig(
            timeframe_value=7,
            timeframe_period='day',
        )

        slack_url = 'https://hooks.slack.com/services'
        alert_config = SlackAlertConfig(slack_url)

        alert_reports = [
            AlertReportConfig(
                report_count=4,
                report_period='day',
                alert_config=alert_config,
            )
        ]

        # Call .create
        with self.assertRaises(ServerException):
            alert.create(
                name=name,
                query=query,
                scope_count=1,
                scope_unit='day',
                increase_positive=True,
                percentage_change=15,
                trigger_config=trigger_config,
                logs=logs,
                alert_reports=alert_reports
            )

    @patch.object(requests.Session, 'post', autospec=True)
    @patch.object(AnomalyAlert, '_create_scheduled_query')
    @patch.object(SpecialAlertBase, '_login')
    def test_create_success(self, mock_login, mock_scheduled_query, mock_post):
        """
        Test .create() passes
        """
        # simulate login
        mock_login.return_value = self.account_id

        mock_scheduled_query.return_value = {
            'scheduled_query': {
                'id': '00000000-0000-03a2-0000-000000000000'
            }
        }

        # Create the response
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 201
        mock_response.text = "Created"
        mock_response.ok = True

        mock_post.return_value = mock_response

        session = requests.session()

        alert = AnomalyAlert(self.username, self.password, session)

        name = 'Too few 404s'
        query = 'where(status=404) calculate(COUNT)'
        logs = [
            '5d481b23-9c4d-4250-bfe8-be389a227f0b',
        ]
        trigger_config = AlertTriggerConfig(
            timeframe_value=7,
            timeframe_period='day',
        )

        slack_url = 'https://hooks.slack.com/services'
        alert_config = SlackAlertConfig(slack_url)

        alert_reports = [
            AlertReportConfig(
                report_count=4,
                report_period='day',
                alert_config=alert_config,
            )
        ]

        # Call .create
        alert.create(
            name=name,
            query=query,
            scope_count=1,
            scope_unit='day',
            increase_positive=False,
            percentage_change=15,
            trigger_config=trigger_config,
            logs=logs,
            alert_reports=alert_reports
        )

        headers = alert.default_headers.copy()
        headers.update({
            'Content-Type': 'application/json;charset=utf-8',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://logentries.com/app/{account_id}'.format(account_id=alert.account_id),
            'X-CSRFToken': alert._get_csrf_token(),
        })

        data = {
            'tag': {
                'actions': [
                    {
                        'enabled': True,
                        'min_report_count': 4,
                        'min_report_period': 'Day',
                        'targets': [{
                            'type': 'slack',
                            'params_set': {
                                'url': slack_url
                            }
                        }],
                        'type': 'Alert',
                    },
                ],
                'name': name[:30],
                'scheduled_query_id': '00000000-0000-03a2-0000-000000000000',
                'sources': [
                    {'id': '5d481b23-9c4d-4250-bfe8-be389a227f0b'}
                ],
                'sub_type': 'AnomalyAlert',
                'type': 'AlertNotify',
                'timeframe_period': 'Day',
                'timeframe_value': 7
            }
        }

        mock_post.assert_called_once_with(
            alert.session,
            url='https://logentries.com/rest/{account_id}/api/tags'.format(
                account_id=alert.account_id
            ),
            headers=headers,
            data=json.dumps(data, sort_keys=True)
        )

        mock_scheduled_query.assert_called_once_with(
            query=query,
            change='-15',
            scope_unit='day',
            scope_count=1,
        )

    @patch.object(SpecialAlertBase, '_api_delete')
    @patch.object(SpecialAlertBase, '_login')
    def test_delete_fails_first(self, mock_login, mock_delete):
        """
        Test .delete() has a failure on first delete
        """
        mock_login.return_value = self.account_id

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Bad Input"
        mock_response.ok = False

        mock_delete.return_value = mock_response

        alert = AnomalyAlert(self.username, self.password)

        with self.assertRaises(ServerException):
            alert.delete(
                '19dede15-118b-467f-bfe9-e9c771d7cc2c',
                '00000000-0000-469c-0000-000000000000'
            )

        mock_delete.assert_called_once_with(
            url='https://logentries.com/rest/{account_id}/api/tags/{tag}'.format(
                account_id=self.account_id,
                tag='19dede15-118b-467f-bfe9-e9c771d7cc2c'
            )
        )

    @patch.object(SpecialAlertBase, '_api_delete')
    @patch.object(SpecialAlertBase, '_login')
    def test_delete_fails_second(self, mock_login, mock_delete):
        """
        Test .delete() has a failure on second delete
        """
        mock_login.return_value = self.account_id

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 500
        mock_response.text = "Bad Input"
        mock_response.ok = False

        mock_delete.side_effect = iter([
            Mock(ok=True),
            mock_response
        ])

        alert = AnomalyAlert(self.username, self.password)

        with self.assertRaises(ServerException):
            alert.delete(
                '19dede15-118b-467f-bfe9-e9c771d7cc2c',
                '00000000-0000-469c-0000-000000000000'
            )

        mock_delete.assert_has_calls(
            [
                call(
                    url='https://logentries.com/rest/{account_id}/api/tags/{tag}'.format(
                        account_id=self.account_id,
                        tag='19dede15-118b-467f-bfe9-e9c771d7cc2c'
                    )
                ),
                call(
                    url='https://logentries.com/rest/{account_id}/api/scheduled_queries/{query_id}'.format(
                        account_id=self.account_id,
                        query_id='00000000-0000-469c-0000-000000000000'
                    )
                ),
            ]
        )

    @patch.object(SpecialAlertBase, '_api_delete')
    @patch.object(SpecialAlertBase, '_login')
    def test_delete_passes(self, mock_login, mock_delete):
        """
        Test .delete() has a failure
        """
        mock_login.return_value = self.account_id

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.ok = True

        mock_delete.return_value = mock_response

        alert = AnomalyAlert(self.username, self.password)

        alert.delete(
            '19dede15-118b-467f-bfe9-e9c771d7cc2c',
            '00000000-0000-469c-0000-000000000000'
        )
        mock_delete.assert_has_calls(
            [
                call(
                    url='https://logentries.com/rest/{account_id}/api/tags/{tag}'.format(
                        account_id=self.account_id,
                        tag='19dede15-118b-467f-bfe9-e9c771d7cc2c'
                    )
                ),
                call(
                    url='https://logentries.com/rest/{account_id}/api/scheduled_queries/{query_id}'.format(
                        account_id=self.account_id,
                        query_id='00000000-0000-469c-0000-000000000000'
                    )
                ),
            ]
        )
