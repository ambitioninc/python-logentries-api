class ConfigurationException(Exception):
    """
    An exception for Configuration errors
    """
    message = 'There was an error in the configuration'


class ServerException(Exception):
    """
    An exception for server errors
    """
    message = 'There was an error from Logentries'
