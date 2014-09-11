History
=======

1.1.1 (11-09-14)
________________

* Renew ssl certs

1.1.0 (05-08-14)
________________

* Add support for google cloud sdk and latest version of gcutil

1.0.0 (24-06-14)
________________

* Extract database out of application folder, move into config folder
* Upgrade database with alembic config
* Major refactor in controllers, remove repeated code
* Add support for configuration profiles

    `$ gstack-configure --profile exampleprofile`

    `$ gstack --profile exampleprofile`

* Give user the ability to debug app

    `$ gstack --debug True`

* Add unittests
* Improve coverage of response attributes

0.1.0 (29-05-14)
________________

* Add GCE GA API support
* Fix error response bugs when resources aren't found


0.0.3 (15-05-2014)
__________________

* Extract config file out of package
* Add binary ``gstack-configure`` at install time


0.0.2 (04-12-2013)
__________________

* Rename to gstack


0.0.1 (24-9-2013)
_________________

* gcloud conception
