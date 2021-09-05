from django.urls import include, path
from django.urls import include, path, re_path

from django.conf import settings

from . import views


_indexable_datasets = []
for _dataset_name in settings.RELATON_DATASETS:
    _indexable_datasets.append(_dataset_name)

re_datasets = f'(?P<dataset_name>{"|".join(_indexable_datasets)})'

urlpatterns = [
    path('v1/', views.index, name='api_index'),
    path('v1/indexers', views.api_list_indexers, name='api_list_indexers'),
    re_path(f'^v1/indexer/{re_datasets}/run', views.api_run_indexer, name='api_run_indexer'),
    re_path(f'^v1/indexer/{re_datasets}/stop', views.api_stop_indexer, name='api_stop_indexer'),
    re_path(f'^v1/indexer/{re_datasets}/reset', views.api_reset_indexer, name='api_reset_indexer'),
    re_path(f'^v1/indexer/{re_datasets}/status', views.api_indexer_status, name='api_indexer_status'),
]

