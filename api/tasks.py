from celery import shared_task


@shared_task
def start_index(lib_name):
    return lib_name
