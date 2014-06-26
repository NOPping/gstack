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

Description
-----------

Apache Cloudstack is open source software designed to deploy and manage large networks of virtual machines, as highly available, highly scalable Infrastructure as a Service(laaS) cloud computing platform. Apache Cloudstack is used by a number of service providers to offer public cloud services, and by many companies to provide an on-premises (private) cloud offering.

Users can manage their Apache Cloudstack cloud with an easy to use web interface, command line tools and/or a full featured RESTful API.

Google Compute Engine is the Infrastructure as a Service (IaaS) component of Google Cloud Platform which is built on the global infrastructure that runs Google's search engine, Gmail, YouTube and other services. Google Compute Engine enables users to launch virtual machines on demand.

Bridging Apache Cloudstack with existing public cloud providers APIs is needed in order to help users work across clouds. Our project’s aim is to create an application that will sit above the Apache Cloudstack API. The application will take in common Google Compute Engine requests, execute the necessary Cloudstack Calls and parse the responses as required. This would allow utilities created for the Google Compute Engine API to be used against Apache Cloudstack. 

Usage
-----

Please see the project wiki for usage instructions (`<https://github.com/NOPping/gstack/wiki>`_)
