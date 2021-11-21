==============
BibXML Indexer
==============

For an overview, see https://github.com/ietf-ribose/bibxml-project.

This project uses Docker, Django, Celery, Redis and PostgreSQL.

.. contents::

.. note::

   Django settings file makes heavy use of environment variables,
   without which project initialization will fail.
   In local development it’s recommended to use Docker Desktop & Docker Compose,
   and currently only that method is covered
   (the old-style conventional way of running under a venv isn’t).


Quick start with Docker Desktop and Compose
-------------------------------------------

Setup
~~~~~

It is required to run Compose from repository root
(.git directory must be present).

Ensure requisite environment variables are configured in the environment.
For convenience, you can place in repository root a file `.env`
with contents like this::

    PORT=8001
    API_SECRET="some-long-random-string"
    DB_NAME=foo
    DB_SECRET="another-long-random-string"
    DJANGO_SECRET="more-long-random-string"
    HOST=localhost
    DEBUG=1

.. important::

   Do not use this environment in production. Refer to operations documentation.

Running
~~~~~~~

From repository root::

    docker compose up

Monitoring logs
~~~~~~~~~~~~~~~

::

    docker compose logs -f -t

Invoking Django management commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    docker compose exec web bash

After which you are in a shell where you can invoke any ``python manage.py <command>``.


Invoking API
~~~~~~~~~~~~

See API spec at http://localhost:8000/api/v1/.

Example request triggering a reindex::

    curl -i -X POST -H "HTTP-X-IETF-token: some-long-random-string" localhost:8001/api/v1/indexer/nist/run

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
                    "git_remote_url": "git://<SOME URL>.git",
                    "git_branch": "main",
                },
                "relaton_data": {
                    "git_branch": "master",
                },
            },
        }

    .. note:: ``relaton_data`` property will be deprecated once ``relaton-bib-py`` library is integrated.
