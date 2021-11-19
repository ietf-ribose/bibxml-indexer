"""View functions for management GUI."""

from django.shortcuts import render
from django.conf import settings
from django.http.request import split_domain_port

from .task_status import get_dataset_task_history


def manage(request):
    return render(request, 'manage.html', dict(
        api_secret=settings.API_SECRET,
        known_datasets=settings.KNOWN_DATASETS,
        task_monitor_host="{}:{}".format(
            split_domain_port(request.get_host())[0],
            5555),
    ))


def manage_dataset(request, dataset_id):
    return render(request, 'manage_dataset.html', dict(
        dataset_id=dataset_id,
        history=get_dataset_task_history(dataset_id),
        api_secret=settings.API_SECRET,
        known_datasets=settings.KNOWN_DATASETS,
    ))
