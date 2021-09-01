from django.http import HttpResponse, JsonResponse

from .tasks import start_index


def index(request):
    return HttpResponse("API v1 index")

from celery.result import AsyncResult


def check_task(request, task_id):
    # TODO:
    # implement celery task check

    # res = AsyncResult(task_id)
    # res.ready()

    return JsonResponse({
        "data":  []
    })


def run_indexer(request, lib):
    # TODO:
    # implement starting celery tasks

    indexer_task = start_index.delay(lib)

    return JsonResponse({
        "data":{
            "indexer": lib,
            "task_id": indexer_task.id
        }
    })
