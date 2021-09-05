import glob
import time
from os import path

import yaml

from celery import shared_task
from django.conf import settings

from indexer.celery import app

from .utils import start_indexation


@shared_task
def run_indexer(dataset_name):
    start_indexation(dataset_name)
