from django.http import HttpResponse, JsonResponse

from celery.result import AsyncResult

from indexer.celery import app

from .task_status import get_task_ids, push_task
from .index import reset_index_for_dataset
from .tasks import run_indexer


def index(request):
    return HttpResponse("API v1 index")


def api_run_indexer(request, dataset_name, refs):
    # TODO: Quickly check sources for given dataset before queueing indexing

    result = run_indexer.delay(dataset_name, refs)
    task_id = result.id

    if (task_id):
        push_task(dataset_name, task_id)

    return JsonResponse({
        "message": "Queued indexing for {} with task ID {}".format(
            dataset_name,
            task_id),
    })


def api_reset_indexer(request, dataset_name):
    reset_index_for_dataset(dataset_name)

    return JsonResponse({
        "message": "Index for {} had been reset".format(dataset_name),
    })


def api_indexer_status(request, dataset_name):
    task_ids = get_task_ids(dataset_name)
    result = []

    for tid in task_ids:
        task = AsyncResult(tid, app=app)
        task_meta = task.info or {}

        task_details = dict(
            task_id=tid,
            status=task_meta.get('status', 'N/A'),
            requested_refs=task_meta.get('requested_refs', 'N/A'))

        total, indexed = \
            task_meta.get('total', None), task_meta.get('indexed', None)

        progress_report = "total: {}, indexed: {}".format(
            total if total is not None else 'N/A',
            indexed if indexed is not None else 'N/A')

        if task.successful():
            date_done = (task.date_done.strftime('%Y-%m-%dT%H:%M:%SZ')
                         if task.date_done
                         else None)
            task_details['outcome_summary'] = \
                "Succeeded ({})".format(progress_report)
            if date_done:
                task_details['completed_at'] = date_done

        elif task.failed():
            task_details['outcome_summary'] = \
                "Failed (error: {}, {}, extended error: {})".format(
                task_meta.get('exc_type', 'N/A'),
                progress_report,
                task_meta.get('exc_message', 'N/A'))

        else:
            progress = {}
            if indexed is not None:
                progress['indexed'] = indexed
            if total is not None:
                progress['total'] = total
            task_details['progress'] = progress

        result.append(task_details)

    return JsonResponse({
        "tasks": result,
    })


def api_stop_task(request, task_id):
    """Revokes and attempts to terminate a task given its ID."""

    task = AsyncResult(task_id, app=app)
    task.revoke(terminate=True)

    return JsonResponse({
        "message": "Task {} has been revoked".format(task_id),
    })


def api_stop_all_tasks(request):
    """Revokes any pending tasks, does not guarantee termination."""

    app.control.purge()

    try:
        # TODO: Check that forced task termination works with stop-all
        jobs = app.control.inspect().active()
        for hostname in jobs:
            tasks = jobs[hostname]
            for task in tasks:
                task = AsyncResult(task['id'], app=app)
                task.revoke(terminate=True)
    except:  # noqa: E722
        return JsonResponse({
            "message": "Pending tasks were revoked, active tasks may remain",
        })
    else:
        return JsonResponse({
            "message": "Pending tasks were revoked",
        })
