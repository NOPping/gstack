# Google Compute Engine Interface For Cloudstack

## Proposal

This project aims to create a new compute API set for Cloudstack that is compatible with Google Compute Engine (GCE). GCE is Google's Infrastructure-as-a-Service (IaaS) compute service that competes with Amazon Web Services EC2.

## Implementation

The GCE APIs for Cloudstack will be supplied as a layer over the current Cloudstack API. The given application will take in a GCE based API request, pass it over to the Cloudstack API, get the required data and return it in a suitable format.
