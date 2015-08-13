from logentries_api.base import Resource
from logentries_api.exceptions import ServerException
import requests


class LogSets(Resource):
    """
    A base class for host-based resources (Old API)
    """

    @property
    def base_url(self):
        return 'https://api.logentries.com/{}/hosts/'.format(self.account_key)

    def list(self):
        """
        Get all log sets

        :return: Returns a dictionary where the key is the hostname or log set,
            and the value is a list of the log keys
        :rtype: dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        response = requests.get(self.base_url)

        if not response.ok:
            raise ServerException(
                '{}: {}'.format(response.status_code, response.text))

        return {
            host.get('name'): [
                log.get('key')
                for log
                in host.get('logs')]
            for host
            in response.json().get('list')
        }

    def get(self, log_set):
        """
        Get a specific log or log set

        :param log_set: The log set or log to get. Ex: `.get(log_set='app')` or
            `.get(log_set='app/log')`
        :type log_set: str

        :returns: The response of your log set or log
        :rtype: dict

        :raises: This will raise a
            :class:`ServerException<logentries_api.exceptions.ServerException>`
            if there is an error from Logentries
        """
        response = requests.get(self.base_url + log_set.rstrip('/'))

        if not response.ok:
            raise ServerException(
                '{}: {}'.format(response.status_code, response.text))
        return response.json()
