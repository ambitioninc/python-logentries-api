"""
Special Alerts use the standard user login authentication rather than a
token-based authentication. For security, it would be more advisable to create
a non-human user account in Logentries and use that email and password
combination for Inactivity and Anomaly Alert creation via the API.


Code Examples
-------------

This example creates an anomaly alert that notifies a slack channel and sends
an email when a higher than normal number of 404's are detected.

.. code-block:: python

    from logentries_api import (
        LogSets, AlertReportConfig, AlertTriggerConfig,
        PagerDutyAlertConfig, SlackAlertConfig,
        AnomalyAlert
    )

    # Create the alert config
    pd_alert = PagerDutyAlertConfig(description='Too many 404s', service_key='...')
    slack_alert = SlackAlertConfig('https://hooks.slack.com/services...')

    # How often to send alerts to the specific alert configs
    alert_report_configs = [
        AlertReportConfig(
            report_count=4,
            report_period='day',
            alert_config=pd_alert
        ),
        AlertReportConfig(
            report_count=1,
            report_period='day',
            alert_config=slack_alert
        ),
    ]

    # How far in the past to compare the anomaly to, in this case, 14 days
    trigger_config = AlertTriggerConfig(
        timeframe_value=14,
        timeframe_period='day'
    )

    # Authenticate into Logentries
    anomaly_alert = AnomalyAlert(
        username='headless_le@yourdomain.com',
        password='...'
    )

    log_sets = LogSets()

    logs = [
        log_sets.get('App1/nginx').get('key'),
        log_sets.get('App2/nginx').get('key'),
    ]

    alert_response = anomaly_alert.create(
        name='Too many 404s!',
        query='where(status=404) calculate(COUNT)',
        scope_count=1,
        scope_unit='day',
        increase_positive=True,
        percentage_change=25,
        trigger_config=trigger_config,
        logs=logs,
        alert_reports=alert_report_configs
    )


This example creates an inactivity alert that notifies a slack channel when
there is no successful web activity for an hour

.. code-block:: python

    from logentries_api import (
        LogSets, AlertReportConfig, AlertTriggerConfig,
        SlackAlertConfig, InactivityAlert
    )

    # Create the alert config
    slack_alert = SlackAlertConfig('https://hooks.slack.com/services...')

    # How often to send alerts to the specific alert configs
    alert_report_configs = [
        AlertReportConfig(
            report_count=1,
            report_period='hour',
            alert_config=slack_alert
        ),
    ]

    # How far in the past to search for inactivity
    trigger_config = AlertTriggerConfig(
        timeframe_value=1,
        timeframe_period='hour'
    )

    # Authenticate into Logentries
    inactivity_alert = InactivityAlert(
        username='headless_le@yourdomain.com',
        password='...'
    )

    log_sets = LogSets()

    logs = [
        log_sets.get('App1/nginx').get('key'),
    ]

    response = inactivity_alert.create(
        name='No web activity',
        patterns=[
            'status=200',
        ],
        logs=logs,
        trigger_config=trigger_config,
        alert_reports=alert_report_configs
    )

"""
from copy import copy
import json
from logentries_api.exceptions import ServerException, ConfigurationException
import requests


class AlertReportConfig(object):
    """
    A class for configuring alert reporting
    """

    def __init__(self, report_count, report_period, alert_config):
        """
        :param report_count: How many times per ``report_period`` to send an
            alert. A number between 1 and 100
        :type report_count: int

        :param report_period: Unit for how often to send the alert. 'day' or
            'hour'
        :type report_period: str

        :param alert_config: An AlertConfig class (Ex:
            ``EmailAlertConfig('me@mydomain.com')``)
        :type alert_config: One of
            :class:`PagerDutyAlertConfig<logentries_api.alerts.PagerDutyAlertConfig>`,
            :class:`WebHookAlertConfig<logentries_api.alerts.WebHookAlertConfig>`,
            :class:`EmailAlertConfig<logentries_api.alerts.EmailAlertConfig>`,
            :class:`SlackAlertConfig<logentries_api.alerts.SlackAlertConfig>`, or
            :class:`HipChatAlertConfig<logentries_api.alerts.HipChatAlertConfig>`
        """

        if report_count < 1 or report_count > 100:
            raise ConfigurationException("Report count must be between 1 and 100")
        self.report_count = report_count

        if report_period.lower() not in ['day', 'hour']:
            raise ConfigurationException("Report period must be 'hour' or 'day'")
        self.report_period = report_period.title()

        self.alert_config = alert_config

    @staticmethod
    def _fix_alert_config_dict(alert_config):
        """
        Fix the alert config .args() dict for the correct key name
        """
        data = alert_config.args()
        data['params_set'] = data.get('args')
        del data['args']
        return data

    def to_dict(self):
        return {
            'min_report_count': self.report_count,
            'min_report_period': self.report_period,
            'type': 'Alert',
            'enabled': True,
            'targets': [
                self._fix_alert_config_dict(self.alert_config)
            ]
        }


class AlertTriggerConfig(object):
    """
    A class for configuring alert triggering
    """

    def __init__(self, timeframe_value, timeframe_period):
        """

        :param timeframe_value: How many 'timeframe_period's to inspect
        :type timeframe_value: int

        :param timeframe_period: The unit for when to inspect. One of
            'minute', 'hour', 'day', 'week'
        :type timeframe_period: str
        """
        if timeframe_value < 1 or timeframe_value > 100:
            raise ConfigurationException(
                "timeframe_value must be between 1 and 100")
        self.timeframe_value = timeframe_value

        if timeframe_period.lower() not in ['minute', 'hour', 'day', 'week']:
            raise ConfigurationException(
                "timeframe_period must be 'minute', 'hour', 'day', or 'week'")
        self.timeframe_period = timeframe_period.title()

    def to_dict(self):
        return {
            'timeframe_period': self.timeframe_period,
            'timeframe_value': self.timeframe_value,
        }


class SpecialAlertBase(object):
    """
    A base class for Inactivity and Anomaly alerts
    """
    default_headers = {
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Host': 'logentries.com'
    }

    def __init__(self, username, password, session=None):
        """
        Authenticate with Logentries with a username and password

        :param username: The email to log in with
        :type username: str
        :param password: The password to log in with
        :type password: str
        :param session: An optional requests session
        :type session: :class:`Session <requests:requests.Session>`

        """
        self.session = session or requests.session()
        self.account_id = self._login(username, password)

    def _get_login_payload(self, username, password):
        """
        returns the payload the login page expects
        :rtype: dict
        """
        payload = {
            'csrfmiddlewaretoken': self._get_csrf_token(),
            'ajax': '1',
            'next': '/app/',
            'username': username,
            'password': password
        }
        return payload

    def _get_csrf_token(self):
        return self.session.cookies.get_dict().get('csrftoken')

    def _get_api_headers(self, **kwargs):
        headers = copy(self.default_headers)
        headers.update({
            'Content-Type': 'application/json;charset=utf-8',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://logentries.com/app/{account_id}'.format(account_id=self.account_id),
            'X-CSRFToken': self._get_csrf_token(),
        })
        headers.update(kwargs)
        return headers

    def _api_post(self, url, **kwargs):
        """
        Convenience method for posting
        """
        response = self.session.post(
            url=url,
            headers=self._get_api_headers(),
            **kwargs
        )
        if not response.ok:
            raise ServerException(
                '{0}: {1}'.format(
                    response.status_code,
                    response.text or response.reason
                ))
        return response.json()

    def _api_delete(self, url, **kwargs):
        """
        Convenience method for deleting
        """
        response = self.session.delete(
            url=url,
            headers=self._get_api_headers(),
            **kwargs
        )
        if not response.ok:
            raise ServerException(
                '{0}: {1}'.format(
                    response.status_code,
                    response.text or response.reason
                ))
        return response

    def _api_get(self, url, **kwargs):
        """
        Convenience method for getting
        """
        response = self.session.get(
            url=url,
            headers=self._get_api_headers(),
            **kwargs
        )
        if not response.ok:
            raise ServerException(
                '{0}: {1}'.format(
                    response.status_code,
                    response.text or response.reason
                ))
        return response.json()

    def _login(self, username, password):
        """
        ._login() makes three requests:

            * One to the /login/ page to get a CSRF cookie
            * One to /login/ajax/ to get a logged-in session cookie
            * One to /app/ to get the beginning of the account id

        :param username: A valid username (email)
        :type username: str
        :param password: A valid password
        :type password: str
        :return: The account's url id
        :rtype: str
        """

        login_url = 'https://logentries.com/login/'
        login_page_response = self.session.get(url=login_url, headers=self.default_headers)
        if not login_page_response.ok:
            raise ServerException(login_page_response.text)

        login_headers = {
            'Referer': login_url,
            'X-Requested-With': 'XMLHttpRequest',
        }
        login_headers.update(self.default_headers)
        login_response = self.session.post(
            'https://logentries.com/login/ajax/',
            headers=login_headers,
            data=self._get_login_payload(
                username,
                password),
        )
        if not login_response.ok:
            raise ServerException(login_response.text)

        app_response = self.session.get('https://logentries.com/app/', headers=self.default_headers)
        return app_response.url.split('/')[-1]

    def list_scheduled_queries(self):
        """
        List all scheduled_queries

        :return: A list of all scheduled query dicts
        :rtype: list of dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        url = 'https://logentries.com/rest/{account_id}/api/scheduled_queries/'.format(
            account_id=self.account_id)
        return self._api_get(url=url).get('scheduled_searches')

    def list_tags(self):
        """
        List all tags for the account.

        The response differs from ``Hooks().list()``, in that tag dicts for
        anomaly alerts include a 'scheduled_query_id' key with the value being
        the UUID for the associated scheduled query

        :return: A list of all tag dicts
        :rtype: list of dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        url = 'https://logentries.com/rest/{account_id}/api/tags/'.format(
            account_id=self.account_id)
        return self._api_get(url=url).get('tags')

    def get(self, name_or_id):
        """
        Get alert by name or id

        :param name_or_id: The alert's name or id
        :type name_or_id: str

        :return: A list of matching tags. An empty list is returned if there are
            not any matches
        :rtype: list of dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        return [
            tag
            for tag
            in self.list_tags()
            if name_or_id == tag.get('id')
            or name_or_id == tag.get('name')
        ]


class InactivityAlert(SpecialAlertBase):
    """
    A class for creating inactivity alerts
    """

    url_template = 'https://logentries.com/rest/{account_id}/api/tags'

    def create(self, name, patterns, logs, trigger_config, alert_reports):
        """
        Create an inactivity alert

        :param name: A name for the inactivity alert
        :type name: str

        :param patterns: A list of regexes to match
        :type patterns: list of str

        :param logs: A list of log UUID's. (The 'key' key of a log)
        :type logs: list of str

        :param trigger_config: A AlertTriggerConfig describing how far back to
            look for inactivity.
        :type trigger_config: :class:`AlertTriggerConfig<logentries_api.special_alerts.AlertTriggerConfig>`

        :param alert_reports: A list of AlertReportConfigs to send alerts to
        :type alert_reports: list of
            :class:`AlertReportConfig<logentries_api.special_alerts.AlertReportConfig>`

        :return: The API response
        :rtype: dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        data = {
            'tag': {
                'actions': [
                    alert_report.to_dict()
                    for alert_report
                    in alert_reports
                ],
                'name': name,
                'patterns': patterns,
                'sources': [
                    {'id': log}
                    for log
                    in logs
                ],
                'sub_type': 'InactivityAlert',
                'type': 'AlertNotify'
            }
        }
        data['tag'].update(trigger_config.to_dict())

        return self._api_post(
            url=self.url_template.format(account_id=self.account_id),
            data=json.dumps(data, sort_keys=True)
        )

    def delete(self, tag_id):
        """
        Delete the specified InactivityAlert

        :param tag_id: The tag ID to delete
        :type tag_id: str

        :raises: This will raise a
            :class:`ServerException <logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        tag_url = 'https://logentries.com/rest/{account_id}/api/tags/{tag_id}'

        self._api_delete(
            url=tag_url.format(
                account_id=self.account_id,
                tag_id=tag_id
            )
        )


class AnomalyAlert(SpecialAlertBase):
    """
    A class for creating AnomalyAlerts
    """

    def _create_scheduled_query(self, query, change, scope_unit, scope_count):
        """
        Create the scheduled query
        """
        query_data = {
            'scheduled_query': {
                'name': 'ForAnomalyReport',
                'query': query,
                'threshold_type': '%',
                'threshold_value': change,
                'time_period': scope_unit.title(),
                'time_value': scope_count,
            }
        }

        query_url = 'https://logentries.com/rest/{account_id}/api/scheduled_queries'

        return self._api_post(
            url=query_url.format(account_id=self.account_id),
            data=json.dumps(query_data, sort_keys=True)
        )

    def create(self,
               name,
               query,
               scope_count,
               scope_unit,
               increase_positive,
               percentage_change,
               trigger_config,
               logs,
               alert_reports):
        """
        Create an anomaly alert. This call makes 2 requests, one to create a
        "scheduled_query", and another to create the alert.

        :param name: The name for the alert
        :type name: str

        :param query: The `LEQL`_ query to use for detecting anomalies. Must
            result in a numerical value, so it should look something like
            ``where(...) calculate(COUNT)``
        :type query: str

        :param scope_count: How many ``scope_unit`` s to inspect for detecting
            an anomaly
        :type scope_count: int

        :param scope_unit: How far to look back in detecting an anomaly. Must
            be one of "hour", "day", or "week"
        :type scope_unit: str

        :param increase_positive: Detect a positive increase for the anomaly. A
            value of ``False`` results in detecting a decrease for the anomaly.
        :type increase_positive: bool

        :param percentage_change: The percentage of change to detect. Must be a
            number between 0 and 100 (inclusive).
        :type percentage_change: int

        :param trigger_config: A AlertTriggerConfig describing how far back to
            look back to compare to the anomaly scope.
        :type trigger_config: :class:`AlertTriggerConfig<logentries_api.special_alerts.AlertTriggerConfig>`

        :param logs: A list of log UUID's. (The 'key' key of a log)
        :type logs: list of str

        :param alert_reports: A list of AlertReportConfig to send alerts to
        :type alert_reports: list of
            :class:`AlertReportConfig<logentries_api.special_alerts.AlertReportConfig>`

        :return: The API response of the alert creation
        :rtype: dict

        :raises: This will raise a
            :class:`ServerException <logentries_api.exceptions.ServerException>`
            if there is an error from Logentries

        .. _Leql: https://blog.logentries.com/2015/06/introducing-leql/

        """
        change = '{pos}{change}'.format(
            pos='+' if increase_positive else '-',
            change=str(percentage_change)
        )

        query_response = self._create_scheduled_query(
            query=query,
            change=change,
            scope_unit=scope_unit,
            scope_count=scope_count,
        )

        scheduled_query_id = query_response.get('scheduled_query', {}).get('id')

        tag_data = {
            'tag': {
                'actions': [
                    alert_report.to_dict()
                    for alert_report
                    in alert_reports
                ],
                'name': name,
                'scheduled_query_id': scheduled_query_id,
                'sources': [
                    {'id': log}
                    for log
                    in logs
                ],
                'sub_type': 'AnomalyAlert',
                'type': 'AlertNotify'
            }
        }
        tag_data['tag'].update(trigger_config.to_dict())

        tag_url = 'https://logentries.com/rest/{account_id}/api/tags'.format(
            account_id=self.account_id
        )

        return self._api_post(
            url=tag_url,
            data=json.dumps(tag_data, sort_keys=True),
        )

    def delete(self, tag_id):
        """
        Delete a specified anomaly alert tag and its scheduled query

        This method makes 3 requests:

            * One to get the associated scheduled_query_id
            * One to delete the alert
            * One to delete get scheduled query

        :param tag_id: The tag ID to delete
        :type tag_id: str

        :raises: This will raise a
            :class:`ServerException <logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        this_alert = [tag for tag in self.list_tags() if tag.get('id') == tag_id]

        if len(this_alert) < 1:
            return

        query_id = this_alert[0].get('scheduled_query_id')

        tag_url = 'https://logentries.com/rest/{account_id}/api/tags/{tag_id}'

        self._api_delete(
            url=tag_url.format(
                account_id=self.account_id,
                tag_id=tag_id
            )
        )
        query_url = 'https://logentries.com/rest/{account_id}/api/scheduled_queries/{query_id}'

        self._api_delete(
            url=query_url.format(
                account_id=self.account_id,
                query_id=query_id
            )
        )
