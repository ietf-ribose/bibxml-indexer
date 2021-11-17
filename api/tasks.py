import traceback
from os import path

from celery.utils.log import get_task_logger

from indexer.celery import app

from .repo import ensure_latest
from .datasets import locate_bibxml_source_repo, locate_relaton_source_repo
from .utils import get_work_dir_path
from .index import index_dataset


logger = get_task_logger(__name__)


@app.task(bind=True)
def run_indexer(task, dataset_id, refs=None):
    """(Re)indexes given dataset.

    :param refs: a list of refs to index,
                 if not provided the entire dataset is indexed

    :returns: an object of the shape
              { total: int,
                indexed: int,
                refs: comma-separated string of requested refs }
    """

    task.update_state(
        state='PROGRESS',
        meta={
            'action': 'starting indexing {}'.format(dataset_id),
            'requested_refs': ','.join(refs or []),
        },
    )

    try:
        bibxml_repo_url, bibxml_repo_branch = \
            locate_bibxml_source_repo(dataset_id)
        bibxml_work_dir_path = get_work_dir_path(
            dataset_id,
            bibxml_repo_url,
            bibxml_repo_branch)

        task.update_state(
            state='PROGRESS',
            meta={
                'action':
                    'pulling or cloning BibXML source '
                    'from {} (branch {}) into {}'
                    .format(
                        bibxml_repo_url,
                        bibxml_repo_branch,
                        bibxml_work_dir_path),
                'requested_refs': ','.join(refs or []),
            },
        )

        ensure_latest(
            bibxml_repo_url,
            bibxml_repo_branch,
            bibxml_work_dir_path)

        bibxml_data_dir = path.join(bibxml_work_dir_path, 'data')

        # TODO: Use relaton-bib-py to generate Relaton data

        relaton_repo_url, relaton_repo_branch = \
            locate_relaton_source_repo(dataset_id)
        relaton_work_dir_path = get_work_dir_path(
            dataset_id,
            relaton_repo_url,
            relaton_repo_branch)

        task.update_state(
            state='PROGRESS',
            meta={
                'action':
                    'pulling or cloning Relaton source '
                    'from {} (branch {}) into {}'
                    .format(
                        relaton_repo_url,
                        relaton_repo_branch,
                        relaton_work_dir_path),
                'requested_refs': ','.join(refs or []),
            },
        )

        ensure_latest(
            relaton_repo_url,
            relaton_repo_branch,
            relaton_work_dir_path)

        relaton_data_dir = path.join(relaton_work_dir_path, 'data')

        update_status = (lambda total, indexed: task.update_state(
                state='PROGRESS',
                meta={
                    'action':
                        'indexing using BibXML data in {} '
                        'and Relaton data in {}'
                        .format(
                            bibxml_data_dir,
                            relaton_data_dir),
                    'total': total,
                    'indexed': indexed,
                    'requested_refs': ','.join(refs or []),
                },
            )
        )

        total, indexed = index_dataset(
            dataset_id,
            bibxml_data_dir,
            relaton_data_dir,
            refs,
            update_status)

        return {
            'total': total,
            'indexed': indexed,
            'requested_refs': ','.join(refs or []),
        }

    except SystemExit:
        logger.exception(
            "Failed to index dataset %s: Task aborted with SystemExit",
            dataset_id)
        traceback.print_exc()
        print("Indexing {}: Task aborted with SystemExit".format(dataset_id))

    except:  # noqa: E722
        logger.exception(
            "Failed to index dataset %s: Task failed",
            dataset_id)
        traceback.print_exc()
        print("Indexing {}: Task failed to complete".format(dataset_id))
        raise
