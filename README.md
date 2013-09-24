[![Build Status](https://travis-ci.org/NOPping/cloudstack-gce.png?branch=master)](https://travis-ci.org/NOPping/cloudstack-gce)

# Google Compute Engine Interface For Cloudstack

## Proposal

This project aims to provide a new compute API interface for Apache Cloudstack that is compatible with Google Compute Engine [GCE](https://cloud.google.com/products/compute-engine). GCE is Google's Infrastructure-as-a-Service (IaaS) compute service that competes with Amazon Web Services EC2. In short, this is a mapping of the GCE API [reference](https://developers.google.com/compute/docs/reference/latest/) and the CloudStack [API](http://cloudstack.apache.org/docs/api/index.html)

## Implementation

The GCE APIs for Cloudstack is supplied as a layer over the current Cloudstack API. The given application will take in a GCE based API request, pass it over to the Cloudstack API, get the required data and return it in a suitable format.

It is written in Python, using [Flask](http://flask.pocoo.org/) to expose a GCE compliant REST API. Requests, Pycrypto, Pyopenssl and Flask-sqlachemy are dependencies. A custom version of pyoauth2 is included in the source.

In this first early release, the following GCE categories are implemented:
- disks
- firewalls
- images
- instances
- machine type
- global operations
- project
- zones

Caveat: There exists some semantic differences between the two APIs, for example between the concept of zones and regions, projects and domains. This project does a best effort attempt at creating a usable GCE interface to a CloudStack cloud but it may not fit every CloudStack deployment.

##Installation

#Developers

Clone the repository

    git clone https://github.com/NOPping/cloudstack-gce.git

Install the package

    python ./setup.py install

This will install a `gcecloudstack` binary in your path. Check the `gcecloudstack/data/config.cfg` and enter the endpoint of your cloud.

Install [gcutil](https://developers.google.com/compute/docs/gcutil/) 

gcloud comes with a self-signed certificate for the local endpoint `gcecloudstack/data/server.crt`, copy the certificate to the gcutil certificates file `gcutil/lib/httplib2/httplib2/cacerts.txt`

At this stage your CloudStack apikey and secretkey need to be entered in the gcutil auth_helper.py file at `gcutil/lib/google_compute_engine/gcutil/auth_helper.py`
This is far from ideal and we opened a featur request with google to pass the `client_id` and `client_secret` as options to gcutil, hopefully future release of gcutil will allow us to do so.

Start gcloud:

    gcecloudstack

Use gcutil with the following parameters (an alias can be useful):

    gcutil --authorization_uri_base=https://localhost:5000/oauth2 --auth_host_name=127.0.0.1 --auth_host_port=9999 --auth_local_webserver=true --api_host="https://localhost:5000/" --fetch_discovery=true

gcutil will issues requests to the local Flask application, get an OAuth token and then issue requests to your CloudStack endpoint

#Users

You can grab the package from Pypi

    pip install gcloud

Then follow the same instructions as the Developers.


##Usage

With a small convenient bash script like this:

    #!/bin/bash

    echo $*

    gcutil --authorization_uri_base=https://localhost:5000/oauth2 --auth_host_name=127.0.0.1 --auth_host_port=9999 --auth_local_webserver=true --api_host="https://localhost:5000/" --fetch_discovery=true $*

You can start issuing standard gcutil commands:

    gcloud --project foobar listmachinetype

##Trouble shooting

If you encounter authentication/authorization issues, clean up your gcutil authentication information `rm -rf ~/.gcutil_auth`, make sure that you set your `client_id` and `client_secret` in `gcutil/lib/google_compute_engine/gcutil/auth_helper.py`

##Apache CloudStack

For more information about CloudStack check the official [website](http://cloudstack.apache.org)

Copyright © 2013 The Apache Software Foundation, Licensed under the Apache License, Version 2.0. 
"Apache", "CloudStack", "Apache CloudStack", and the Apache feather logos are registered trademarks or trademarks of The Apache Software Foundation.