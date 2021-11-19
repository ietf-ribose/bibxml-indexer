from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.urls import path, include
from django.views.decorators.http import require_POST, require_safe

from main import api, views

from .views import openapi_spec, auth, basic_auth


urlpatterns = [
    path('admin/', admin.site.urls),

    path('openapi.yaml', require_safe(openapi_spec)),

    path('api/', include([
        path('v1/', include([
            path('',
                 require_safe(api.index),
                 name='api_index'),
            path('indexer/', include([
                path('<dataset_name>/', include([
                    path('run/',
                         csrf_exempt(require_POST(auth(api.run_indexer))),
                         name='api_run_indexer'),
                    path('reset/',
                         csrf_exempt(require_POST(auth(api.reset_index))),
                         name='api_reset_index'),
                    path('status/',
                         require_safe(auth(api.indexer_status)),
                         name='api_indexer_status'),
                ])),
            ])),
            path('tasks/', include([
                path('<task_id>/stop/',
                     csrf_exempt(require_POST(auth(api.stop_task))),
                     name='api_stop_task'),
                path('stop-all/',
                     csrf_exempt(require_POST(auth(api.stop_all_tasks))),
                     name='api_stop_all_tasks'),
            ])),
        ])),
    ])),

    path('', include([
        path('',
             require_safe(basic_auth(views.manage)),
             name='manage'),
        path('<dataset_id>/', include([
            path('',
                 require_safe(basic_auth(views.manage_dataset)),
                 name='manage_dataset'),
        ])),
    ])),
]
