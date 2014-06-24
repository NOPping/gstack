======
GSTACK
======

A Google Compute Engine Interface For Cloudstack
################################################

.. image:: https://badge.fury.io/py/gstack.png
       :target: https://pypi.python.org/pypi/gstack
.. image:: https://api.travis-ci.org/NOPping/gstack.png?branch=master
       :target: https://travis-ci.org/NOPping/gstack
.. image:: https://coveralls.io/repos/NOPping/gstack/badge.png?branch=master
       :target: https://coveralls.io/r/NOPping/gstack



Proposal
_________

This project aims to provide a new compute API interface for Apache Cloudstack that is compatible with Google Compute Engine `GCE <https://cloud.google.com/products/compute-engine>`_,  GCE is Google's Infrastructure-as-a-Service (IaaS) compute service that competes with Amazon Web Services EC2. In short, this is a mapping of the `GCE API <https://developers.google.com/compute/docs/reference/latest/>`_ and the `CloudStack API <http://cloudstack.apache.org/docs/api/index.html>`_

Implementation
______________

The GCE APIs for Cloudstack is supplied as a layer over the current Cloudstack API. The given application will take in a GCE based API request, pass it over to the Cloudstack API, get the required data and return it in a suitable format.

It is written in Python, using `Flask <http://flask.pocoo.org/>`_ to expose a GCE compliant REST API. Requests, Pycrypto, Pyopenssl and Flask-sqlachemy are dependencies. A custom version of pyoauth2 is included in the source.

- Disks
   - listdisks
   - getdisk
- Firewalls
   - addfirewall
   - deletefirewall
   - listfirewalls
   - getfirewall
- Images
   - listimages
   - getimage
- Instances
   - addinstance
   - deleteinstance
   - listinstances
   - getinstance
- Machinetypes
   - listmachinetypes
   - getmachinetype
- Project
   - getproject
- Zones
   - listzones
   - getzone


Installation
############

Developers
__________

Clone the repository

    $ git clone https://github.com/NOPping/gstack.git

Install the package

    $ python ./setup.py install

Users
_____

Users can grab the package from Pypi

    $ pip install gstack

Configuration
#############

Before running gstack you must configure it. To do so run

    $ gstack-configure

You can configure a profile of your choice with the optional ``-p`` or ``--profile`` flag

    $ gstack-configure -p exampleprofile

If you don't specify a profile, ``gstack-configure`` will default to ``initial``

Enter your configuration information as prompted.

Install the stand alone `gcutil <https://developers.google.com/compute/docs/gcutil/#gcutilupgrade/>`_

gstack comes with a self-signed certificate for the local endpoint ``gstack/data/server.crt``, copy the certificate to the gcutil certificates file ``gcutil/lib/httplib2/httplib2/cacerts.txt``

At this stage your CloudStack apikey and secretkey need to be entered in the gcutil auth_helper.py file at ``gcutil/lib/google_compute_engine/gcutil/auth_helper.py``

This is far from ideal and we opened a feature request with google to pass the ``client_id`` and ``client_secret`` as options to gcutil, hopefully future release of gcutil will allow us to do so.

Create a cached parameters file for gcutil:

- Make a flagfile to store required flags, something like ``~/.gcutil_params``

- An example of what to put in here would be:

    `--auth_local_webserver`
    
    `--auth_host_port=9999`
    
    `--dump_request_response`
    
    `--authorization_uri_base=https://localhost:5000/oauth2`
    
    `--ssh_user=root`
    
    `--fetch_discovery`
    
    `--auth_host_name=localhost`
    
    `--api_host=https://localhost:5000/`
    
    `--nocheck_for_new_version`

    `--permit_root_ssh`

gcutil will issue auth requests to the local Flask application, get an OAuth token and then issue requests to the CloudStack endpoint you specified when cofiguring gstack. 

Usage
#####

Start gstack:

    $ gstack

You can launch gstack using a configuration profile created earlier using the optional ``-p`` or ``--profile`` flag

    $ gstack -p exampleprofile

If you don't specify a profile, gstack will default to ``initial``

You can start gstack in debug mode using the optional ``-d`` or ``--debug`` flag

    $ gstack -d True

You can now start issuing standard gcutil commands to gstack.

    $ ./gcutil --flag_file=~/.gcutil_params --project=brogand93@darrenbrogan.ie listzones


==================   ========  ====================
name                  status   next-maintenance 
==================   ========  ====================
Sandbox-simulator     UP       None scheduled   
==================   ========  ====================

Running The Tests
#################

To run the included tests the following software is required:

   pep8
   
   pylint
   
   nose
   
   mock
   
   coverage

These can be installed via the Python Package Index:

   $ pip install pep8 pylint nose mock coverage

Tests can be executed from the root of the code base as follows:

Style Check
___________

   $ pep8 --ignore=E501 *.py gstack

Lint
____

   $ pylint --rcfile=pylint.rc *.py gstack

Unit Tests
__________

   $ nosetests --with-coverage  --cover-erase --cover-package=gstack --cover-html

A HTML base coverage report will be placed in ./cover

Trouble shooting
################

CertificateHostnameMismatch
___________________________

- Ensure that the addresses you entered for ``authorization_uri_base``, ``api_host`` and ``auth_host_name`` are the exact same as the address you binded ``gstack`` to earlier when configuring with ``gstack-configure``.

Authentication/authorization issues
___________________________________

- Clean up your gcutil authentication information ``rm -rf ~/.gcutil_auth``.
- Ensure that you set your ``client_id`` and ``client_secret`` in ``gcutil/lib/google_compute_engine/gcutil/auth_helper.py``.



Apache CloudStack
#################

For more information about CloudStack check the official `<website http://cloudstack.apache.org>`_

Copyright © 2013 The Apache Software Foundation, Licensed under the Apache License, Version 2.0.
"Apache", "CloudStack", "Apache CloudStack", and the Apache feather logos are registered trademarks or trademarks of The Apache Software Foundation.

