"""A Redis cache is used to keep track of Celery task IDs and dataset IDs
they operate on.

This means if Redis is down, we may lose this correspondence,
but Celery-provided admin UI can still be used to monitor status of tasks
(just without dataset correspondence)."""

from . import cache


def get_task_ids(dataset_id, limit=10):
    """Retrieves Celery task IDs for dataset indexing runs,
    ordered from most recently started to least recently started.

    :param dataset_id: dataset ID
    :param limit: how many task IDs to return, by default 10 most recent
    :returns: list of task IDs as strings"""

    return cache.lrange(dataset_id, 0, limit)


def push_task(dataset_id, task_id):
    """Adds given ``task_id`` to the top of the list for given dataset,
    and sets a key with task metadata (currently, requested refs).

    :param task_id: Celery task ID."""

    cache.lpush(dataset_id, task_id)
