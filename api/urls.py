from django.urls import include, path
from django.urls import include, path, re_path

from . import views

_libs = ["rfc", "id", "std", "bcp", "fyi", "nist"]
re_libs = f'(?P<lib>{"|".join(_libs)})'

urlpatterns = [
    path('v1/', views.index, name='api_index'),
    path(f'v1/task/<str:task_id>', views.check_task, name='api_check_task'),
    re_path(f'^v1/indexer/{re_libs}/run', views.run_indexer, name='api_run_indexer'),
]
