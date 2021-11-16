from django.urls import path, re_path
from . import views


urlpatterns = [
    path('v1/', views.index, name='api_index'),

    re_path(r'^v1/indexer/(?P<dataset_name>[\w-]+)/run',
            views.api_run_indexer,
            name='api_run_indexer'),
    re_path(r'^v1/indexer/(?P<dataset_name>[\w-]+)/reset',
            views.api_reset_indexer,
            name='api_reset_indexer'),
    re_path(r'^v1/indexer/(?P<dataset_name>[\w-]+)/status',
            views.api_indexer_status,
            name='api_indexer_status'),

    re_path(r'^v1/tasks/(?P<task_id>[\w-]+)/stop',
            views.api_stop_task,
            name='api_stop_task'),
    re_path(r'^v1/tasks/stop-all',
            views.api_stop_all_tasks,
            name='api_stop_all_tasks'),
]
