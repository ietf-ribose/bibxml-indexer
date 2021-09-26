from django.http import HttpResponse, JsonResponse

from django.conf import settings

from .tasks import run_indexer
from .utils import (
    start_indexation,
    reset_indexation,
    stop_indexation,
    get_index_info,
    task_status,

)


from . import RD


def index(request):
    return HttpResponse("API v1 index")


def api_run_indexer(request, dataset_name):

    if task_status(dataset_name) != "running":
        indexer_task = run_indexer.delay(dataset_name)
        RD.hset(dataset_name, "task_id", indexer_task.id)

        return JsonResponse(
            {"data": {}}
        )
    else:
        return JsonResponse(
            {
                "error": {
                    "code": 0,
                    "message": "%s indexation already running" % dataset_name,
                }
            },
            status=500
        )


def api_stop_indexer(request, dataset_name):

    if task_status(dataset_name) == "running":

        task_id = stop_indexation(dataset_name)

        return JsonResponse(
            {
                "data": {
                    "message": "indexing '%s' task (%s) has been stopped"
                    % (dataset_name, task_id),
                }
            }
        )
    else:
        return JsonResponse(
            {
                "error": {
                    "code": 0,
                    "message": "'%s' indexation is not running" % dataset_name,
                }
            },
            status=500
        )


def api_reset_indexer(request, dataset_name):

    reset_indexation(dataset_name)

    return JsonResponse(
        {
            "data": {
                "message": "'%s' index has been reset" % dataset_name,
            }
        }
    )


def api_indexer_status(request, dataset_name):

    dataset = settings.RELATON_DATASETS.get(dataset_name, False)

    if dataset:
        index_info = get_index_info(dataset_name)
        return JsonResponse({"data": index_info})

    else:
        return JsonResponse({"error": {
            "code": 0,
            "message": "Unknown dataset name: %s" % dataset_name
        }}, status=404)


def api_list_indexers(request):

    indexable_datasets = {}

    for _name in settings.RELATON_DATASETS:
        indexable_datasets[_name] = get_index_info(_name)

    return JsonResponse({"data": indexable_datasets})
