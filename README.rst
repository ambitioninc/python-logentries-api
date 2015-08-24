.. image:: https://travis-ci.org/ambitioninc/python-logentries-api.png
   :target: https://travis-ci.org/ambitioninc/python-logentries-api

.. image:: https://coveralls.io/repos/ambitioninc/python-logentries-api/badge.png?branch=master
    :target: https://coveralls.io/r/ambitioninc/python-logentries-api?branch=master

python-logentries-api
=====================
This is a Python wrapper for the Logentries API. The API object terms follow
the semantics from the Logentries website, not the Logentries API.

The `InactivityAlert`_ and `AnomalyAlert`_ classes simulate a user login to
create the appropriate alerts.

.. _AnomalyAlert: http://python-logentries-api.readthedocs.org/en/latest/ref/special_alerts.html#anomalyalert
.. _InactivityAlert: http://python-logentries-api.readthedocs.org/en/latest/ref/special_alerts.html#inactivityalert

This is not endorsed or provided by Logentries, and no commercial support is
provided.

Example
-------

To create a new tag called 'user_agent = curl' and associate it with a log
called 'someset/somelog':

::

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


Installation
------------
To install the latest release, type::

    pip install python-logentries-api

To install the latest code directly from source, type::

    pip install git+git://github.com/ambitioninc/python-logentries-api.git

Documentation
-------------

Full documentation is available at http://python-logentries-api.readthedocs.org

License
-------
MIT License (see LICENSE)
