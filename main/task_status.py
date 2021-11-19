"""A Redis cache is used to keep track of Celery task IDs and dataset IDs
they operate on.

This means if Redis is down, we may lose this correspondence,
but Celery-provided admin UI can still be used to monitor status of tasks
(just without dataset correspondence)."""

import traceback

from celery.result import AsyncResult

from indexer.celery import app

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


def get_dataset_task_history(dataset_name, limit=10):
    task_ids = get_task_ids(dataset_name, limit)
    tasks = []

    for tid in task_ids:
        result = AsyncResult(tid, app=app)
        task = dict(task_id=tid, status=result.status)

        meta = result.info or {}

        if isinstance(meta, Exception):
            task['error'] = dict(
                type=getattr(meta.__class__, '__name__', 'N/A'),
                message='\n'.join(traceback.format_exception(
                    meta.__class__,
                    meta,
                    meta.__traceback__)))

        else:
            refs = meta.get('requested_refs', None)
            task['requested_refs'] = refs.split(',') if refs else None

            total, indexed = \
                meta.get('total', None), meta.get('indexed', None)

            if result.successful():
                task['outcome_summary'] = \
                    "Succeeded (total: {}, indexed: {})".format(
                        total if total is not None else 'N/A',
                        indexed if indexed is not None else 'N/A')
                if result.date_done:
                    task['completed_at'] = \
                        result.date_done.strftime('%Y-%m-%dT%H:%M:%SZ')

            elif result.failed():
                err_msg = meta.get('exc_message', ['N/A'])
                task['error'] = dict(
                    type=meta.get('exc_type', 'N/A'),
                    message='\n'.join(err_msg)
                            if isinstance(err_msg, list)
                            else repr(err_msg),
                )

            else:
                task['action'] = meta.get('action', 'N/A')
                progress = {}
                if indexed is not None:
                    progress['indexed'] = indexed
                if total is not None:
                    progress['total'] = total
                task['progress'] = progress

        tasks.append(task)

    return tasks
