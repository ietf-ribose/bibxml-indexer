import glob
import time
from os import path, access, makedirs, F_OK, R_OK, W_OK

import yaml

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError

from django.conf import settings

from indexer.celery import app

from .models import RefData
from . import RD


# to avoid date errors
yaml.SafeLoader.yaml_implicit_resolvers = {
    k: [r for r in v if r[0] != "tag:yaml.org,2002:timestamp"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def task_status(dataset_name, status=False):
    if settings.RELATON_DATASETS.get(dataset_name, False):
        if status:
            RD.hset(dataset_name, "status", status)
            return status #.decode("utf8")
        else:
            result = RD.hget(dataset_name, "status")
            if result:
                return result #.decode("utf8")
            else:
                return ""
    else:
        return ""


def task_start(dataset_name):
    if settings.RELATON_DATASETS.get(dataset_name, False):
        RD.hset(dataset_name, "status", "running")
        RD.hset(dataset_name, "started_at", time.time())
        RD.hset(dataset_name, "stopped_at", "")
        RD.hset(dataset_name, "message", "")


def task_successful(dataset_name):
    if settings.RELATON_DATASETS.get(dataset_name, False):
        RD.hset(dataset_name, "status", "completed")
        RD.hset(dataset_name, "message", "")
        RD.hset(dataset_name, "task_id", "")
        RD.hset(dataset_name, "stopped_at", time.time())


def task_abort(dataset_name, err_message=""):
    if settings.RELATON_DATASETS.get(dataset_name, False):
        RD.hset(dataset_name, "status", "failed")
        RD.hset(dataset_name, "stopped_at", time.time())

        if err_message:
            RD.hset(dataset_name, "message", err_message)

    return False, err_message


def start_indexation(dataset_name):
    success, message = _prepare_repo(dataset_name, True)
    if success:
        data_dir = message
        try:
            _do_indexation(dataset_name, data_dir)
            task_successful(dataset_name)
        except Exception as err:
            err_message = "Indexation failed: %s" % err
            task_abort(dataset_name, err_message)
            # raise err


def _do_indexation(dataset_name, data_dir):
    if path.exists(data_dir):

        lst = glob.glob("%s/*.yaml" % data_dir)

        i = 0
        exists_ids = []
        for yaml_fname in lst:
            with open(yaml_fname, "r", encoding="utf-8") as fhandler:
                try:
                    ref_data = yaml.load(
                        fhandler.read(), Loader=yaml.SafeLoader
                    )

                    docid = ref_data.get("docid", None)
                    ref_type = ref_data.get("doctype", None)

                    if docid:
                        ref_id = docid.get("id", None)

                    if ref_id:
                        exists_ids.append(ref_id)
                        ref_obj = RefData.objects.update_or_create(
                            ref_id=ref_id,
                            ref_type=ref_type,
                            dataset=dataset_name,
                            body=ref_data,
                        )

                        i += 1

                        RD.hset(dataset_name, "indexed_files", i)
                    else:
                        # TODO:
                        # write error to log?
                        pass

                except Exception as err:
                    # log()
                    # print(bib_id, ref_data, err)
                    pass

        # Remove all objects of this dataset (except indexed now)
        RefData.objects.filter(dataset=dataset_name).exclude(
            ref_id__in=exists_ids
        ).delete()



def _prepare_repo(dataset_name, do_pull=False):
    dataset = settings.RELATON_DATASETS.get(dataset_name, False)

    if dataset and task_status(dataset_name) != "running":

        task_start(dataset_name)

        git_remote_url = dataset.get("git_remote_url", False)
        if not git_remote_url and isinstance(git_remote_url, str):
            err_message = "Settings error: git_remote_url empty or not str"
            return task_abort(dataset_name, err_message)

        git_branch = dataset.get("git_branch", False)
        if not git_branch and isinstance(git_branch, str):
            err_message = "Settings error: git_branch empty or not str"
            return task_abort(dataset_name, err_message)

        local_repo_dir = dataset.get("local_repo_dir", False)
        if not git_branch and isinstance(local_repo_dir, str):
            err_message = "Settings error: local_repo_dir empty or not str"
            return task_abort(dataset_name, err_message)

        repo_dir = "%s/%s" % (
            settings.PATH_TO_DATA_DIR,
            local_repo_dir,
        )

        data_dir = "%s/data" % repo_dir

        if not access(settings.PATH_TO_DATA_DIR, W_OK):
            err_message = "Project data directory is not writable"
            return task_abort(dataset_name, err_message)

        if not access(repo_dir, F_OK):
            makedirs(repo_dir)

        if not access(repo_dir, W_OK):
            err_message = "Repo directory is not writable"
            return task_abort(dataset_name, err_message)

        if not access("%s/.git/config" % repo_dir, F_OK):
            try:
                Repo.clone_from(
                    git_remote_url,
                    repo_dir,
                    branch=git_branch,
                )
            except GitCommandError as err:
                RD.hdel(dataset_name, "commit")
                err_message = "Unable to clone git repo: %s.\n%s" % (
                    git_remote_url,
                    err,
                )
                return task_abort(dataset_name, err_message)
        try:
            repo = Repo(repo_dir)
        except InvalidGitRepositoryError as err:
            RD.hdel(dataset_name, "commit")
            err_message = "Unable to init git repo at dir: %s" % repo_dir
            return task_abort(dataset_name, err_message)

        if not access(data_dir, R_OK):
            err_message = "Unable to read repo 'data' directory"
            return task_abort(dataset_name, err_message)

        if "origin" in repo.remotes:

            # TODO:
            # normalize urls?
            # ignore protocols?
            #
            # if git_remote_url != repo.remotes.origin.url:
            #    return (
            #        False,
            #        "Git remote URL and configuration is not same: \n%s\n%s"
            #        % (git_remote_url, repo.remotes.origin.url),
            #    )

            if do_pull:
                try:
                    cmd_result = repo.remotes.origin.pull()
                except GitCommandError as err:
                    err_message = "Failed git pull: %s" % err
                    return task_abort(dataset_name, err_message)

            head = repo.heads[0]

            if head.name != git_branch:
                err_message = (
                    "Current git branch is '%s', settings expects: '%s'"
                    % (head.name, git_branch)
                )
                return task_abort(dataset_name, err_message)

            RD.hset(dataset_name, "commit", head.commit.hexsha)

            return True, data_dir

        else:
            RD.hdel(dataset_name, "commit")
            err_message = "Unable get origin in repo remotes"
            return task_abort(dataset_name, err_message)

    elif task_status(dataset_name) != "running":
        return False, "Task '%s' is locked now" % dataset_name
    else:
        return False, "Unknown dataset: %s, check settings" % dataset_name


def reset_indexation(dataset_name):

    stop_indexation(dataset_name)
    RefData.objects.filter(dataset=dataset_name).delete()
    # TODO:
    # remove git repo?


def stop_indexation(dataset_name):
    task_id = RD.hget(dataset_name, "task_id")

    RD.hset(dataset_name, "task_id", "")
    RD.hset(dataset_name, "status", "")
    RD.hset(dataset_name, "message", "")
    RD.hset(dataset_name, "started_at", "")
    RD.hset(dataset_name, "stopped_at", "")
    RD.hset(dataset_name, "indexed_files", "0")
    RD.hset(dataset_name, "commit", "")

    if task_id:
        app.control.revoke(task_id, terminate=True)

    return task_id


def get_index_info(dataset_name):

    empty = {
        "task_id": "",
        "status": "",
        "started_at": "",
        "stopped_at": "",
        "indexed_files": "0",
        "message": "",
        "commit": "",
    }

    redis_data = RD.hgetall(dataset_name)
    dataset_info = {**empty, **redis_data}

    return dataset_info 
