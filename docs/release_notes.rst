Release Notes
=============

v0.7
----

* Removed length restriction on special alert names
* Added ``.get()``, ``.list_tags()``, and ``.list_scheduled_queries()`` methods for special alerts
* Changed signature on ``AnomalyAlert().delete()`` to only require the tag_id

v0.6
----

* Added ``.delete()`` to ``AnomalyAlert`` and ``InactivityAlert``

v0.5
----

* Changed names of AlertConfig classes
* Added ``AnomalyAlert`` and ``InactivityAlert``

v0.4
----

* Added ``.get()`` and ``.update()``  methods to resources
* Modified ``publish.py`` script to upload wheel that is built from sdist

v0.3
----

* Updated log api to https

v0.2
----

* Added delete methods to resources

v0.1
----

* This is the initial release of python-logentries-api.
