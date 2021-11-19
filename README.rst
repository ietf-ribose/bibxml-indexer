============================
BibXML indexer service & API
============================

For an overview, see https://github.com/ietf-ribose/bibxml-project.

This project uses Docker, Django, Celery, Redis and PostgreSQL.

.. note::

   Django settings file makes heavy use of environment variables,
   without which project initialization will fail.
   In local development it’s recommended to use Docker Desktop & Docker Compose,
   and currently only that method is covered
   (the old-style conventional way of running under a venv isn’t).


Running locally using Docker Desktop and Compose
------------------------------------------------

Ensure requisite environment variables are configured in the environment.
For convenience, you can put a file .env with contents like this::

    PORT=8001
    DB_NAME=foo
    DB_SECRET="some-long-random-string"
    DJANGO_SECRET="another-long-random-string"
    HOST=localhost

.. important::

   DEBUG must not be set to 1 in production.

Then, run ``docker compose up`` from repository root.

To check successful deployment, navigate to http://localhost:8000/api/v1/.

Invoking Django management commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    % docker compose exec web bash

After which you are in a shell where you can invoke any ``python manage.py <command>``.

Using the API
-------------

An indexing task can be added to queue by querying an API endpoint
of the form `<indexer domain>/api/v1/indexer/<dataset ID>/run`.

For example::

    curl http://127.0.0.1:8001/api/v1/indexer/nist/run

With properly configured infrastructure across bibxml-service and bibxml-indexer,
given dataset will be indexed into a database accessible by bibxml-service APIs.


Datasets
--------

These are the currently available datasets:

* ``rfcs`` (bibxml)
* ``ids`` (bibxml3)
* ``rfcsubseries`` (bibxml9)
* ``misc`` (bibxml2)
* ``w3c`` (bibxml4)
* ``3gpp`` (bibxml5)
* ``ieee`` (bibxml6)
* ``iana`` (bibxml8)
* ``doi`` (bibxml9)
* ``nist`` (no existing id)



Dataset sources
---------------

By default,

* ``bibxml-data-{dataset_id}`` repositories under ``ietf-ribose`` Github user are treated as BibXML sources, and
* ``relaton-data-{dataset_id}`` repositories under ``relaton`` Github user are treated as Relaton sources
  (until ``relaton-bib-py`` library takes care of conversion).

Default branch is main.

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
