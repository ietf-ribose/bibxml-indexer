import glob
import time
from os import path

import yaml

from celery import shared_task
from django.conf import settings

from .models import BibData


@shared_task
def start_index(lib_name):

    data_dir = '%s/relaton-data-%s/data' % (settings.PATH_TO_DATA_DIR, lib_name)

    if path.exists(data_dir):
        lst = glob.glob('%s/*.yaml' % data_dir)
        for yaml_fname in lst:
            with open(yaml_fname, "r", encoding="utf-8") as fhandler:
                bib_data = yaml.load(fhandler.read(), Loader=yaml.SafeLoader)

                bib_obj = BibData.objects.create(
                    bib_id=bib_data['id'],
                    bib_type=lib_name,
                    body=bib_data
                )


    return lst
