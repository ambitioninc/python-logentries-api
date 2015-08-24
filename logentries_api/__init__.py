# flake8: noqa
from logentries_api.resources import Tags, Labels, Hooks, Alerts
from logentries_api.logs import LogSets
from logentries_api.alerts import (
    PagerDutyAlertConfig, EmailAlertConfig, WebHookAlertConfig,
    SlackAlertConfig, HipChatAlertConfig
)

from logentries_api.special_alerts import (
    AlertReportConfig, AlertTriggerConfig,
    InactivityAlert, AnomalyAlert
)
