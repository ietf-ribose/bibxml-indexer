==============
BibXML Indexer
==============

For an overview, see https://github.com/ietf-ribose/bibxml-project.

This project uses Docker, Django, Celery, Redis and PostgreSQL.

.. contents::

.. note::

   Django settings file makes heavy use of environment variables,
   without which project initialization will fail.
   In local development it’s recommended to use Docker Desktop & minikube,
   and currently only that method is covered.


Quick start with Docker Desktop and minikube
--------------------------------------------

Prerequisite
~~~~~~~~~~~~

* Install Docker Docker

* Install minikube (a tool for running Kubernetes locally)


Using minikube
~~~~~~~~~~~~~~

Run Docker Desktop.

Start minikube ::

    minikube start

Start Minikube with logs ::

    minikube start --driver=docker --alsologtostderr


Show minikube dashboard in browser ::

    minikube dashboard --url=false


Clear local state ::

    minikube delete


Steps to test bibxml-indexer and bibxml-service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go to bibxml-indexer source folder ::

    cd ~/path/to/bibxml-indexer

Start minikube ::

    minikube start

Set docker environment ::

    eval $(minikube -p minikube docker-env)

Show minikube dashboard ::

    minikube dashboard --url=false

Create redis, db, network, secret in Kubernetes in a new terminal ::

    eval $(minikube -p minikube docker-env)
    kubectl apply -f k8s/redis
    kubectl apply -f k8s/db
    kubectl apply -f k8s/network
    kubectl apply -f k8s/secret

Check whether pods, services and secrets are set up properly ::

    kubectl get po,svc,secret


Build docker image locally ::

    docker build -t bibxml/base .

Apply db migration ::

    kubectl apply -f k8s/job/db-migration.yaml

Check migration is completed ::

    kubectl get po

Remove completed job (Optional) ::

    kubectl delete -f k8s/job/db-migration.yaml

Create web, celery, flower ::

    kubectl apply -f k8s/web
    kubectl apply -f k8s/celery
    kubectl apply -f k8s/flower

Check whether pods and services ::

    kubectl get po,svc

Go to bibxml-service source folder ::

    cd ~/path/to/bibxml-service

Create bibxml-service in a new terminal ::

    eval $(minikube -p minikube docker-env)
    kubectl apply -f k8s/ws

Check whether bibxml-service is running ::

    kubectl get po,svc

.. important::

   Do not use this secrets and environment in production. Refer to operations documentation.

   Secret and environment variables are store in YAML files under k8s folder.

   Some secrets are encoded in base64 format.


Monitoring logs
~~~~~~~~~~~~~~~

Check names and statuses of pods ::

    kubectl get po

Get logs ::

    kubectl logs <name_of_pod>


Invoking Django management commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    kubectl run -i --tty --attach web --image=bibxml/base --image-pull-policy=Never -- sh

After which you are in a shell where you can invoke any ``python manage.py <command>``.


Invoking API
~~~~~~~~~~~~

See API spec at http://localhost:8001/api/v1/.

Example request triggering a reindex::

    curl -i -X POST -H "X-IETF-token: some-long-random-string" localhost:8001/api/v1/indexer/nist/run

With properly configured infrastructure across bibxml-service and bibxml-indexer,
given dataset will be indexed into a database accessible by bibxml-service instance.


Authentication
~~~~~~~~~~~~~~

API endpoints require a token
that matches ``API_SECRET`` environment variable at deploy time
to be provided in ``HTTP_X_IETF_TOKEN`` header of each request.

Management GUI is exposed under HTTP Basic auth,
and requires the user to specify "ietf" as username
and the above API secret as password.


Dataset sources
---------------

Indexer accepts any string as dataset ID,
but if indexing is requested for nonexistent dataset,
indexing will fail due to missing source data.

By default,

* ``bibxml-data-{dataset_id}`` repositories under ``ietf-ribose`` Github user are treated as BibXML sources, and
* ``relaton-data-{dataset_id}`` repositories under ``relaton`` Github user are treated as Relaton sources
  (until ``relaton-bib-py`` library takes care of conversion).

Default branch name is ``main``.

.. seealso:: ``DATASET_SOURCE_OVERRIDES`` setting.

.. note::

   BibXML data repositories should contain a set of files
   named ``<citation_ref>.xml`` under ``<repo_root>/data/``.

   Relaton data repositories should contain a set of files
   named ``<citation_ref>.yaml`` under ``<repo_root>/data/``.


Django settings
---------------

``indexer.settings.DATASET_TMP_ROOT``
    Where to keep fetched source data and data generated during indexing.

``indexer.settings.KNOWN_DATASETS``
    A list of known dataset IDs.

``indexer.settings.AUTHORITATIVE_DATASETS``
    A list of dataset IDs corresponding to IETF authoritative datasets.

``indexer.settings.API_USER``
    Username that will be required by GUI using HTTP Basic authentication.

``indexer.settings.API_SECRET``
    Secret that will be required in header to trigger API endpoints,
    and as password for HTTP Basic authentication when using GUI.

``indexer.settings.DATASET_SOURCE_OVERRIDES``
    This setting can be used to override sources for a dataset
    by mapping dataset ID to dataset source configuration.
    
    It can partially override only one of the sources (bibxml or relaton),
    and for that source only branch name or only URL;
    or it can override everything for given dataset.
    
    For example::

        DATASET_SOURCE_OVERRIDES = {
            "ecma": {
                "bibxml_data": {
                    "repo_url": "git://<SOME URL>.git",
                    "repo_branch": "main",
                },
                "relaton_data": {
                    "repo_branch": "master",
                },
            },
        }

    .. note:: ``relaton_data`` property will be deprecated once ``relaton-bib-py`` library is integrated.


Credits
-------

Authored by Ribose as produced under the IETF BibXML SOW.
