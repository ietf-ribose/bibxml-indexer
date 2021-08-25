from django.http import HttpResponse, JsonResponse

from .tasks import start_index


def index(request):
    return HttpResponse("API v1 index")


def check_task(request, id):
    # TODO:
    # implement celery task check

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
