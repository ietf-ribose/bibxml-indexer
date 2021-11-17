"""Utilities for dealing with Git."""

from os import access, path, rmdir, R_OK
from git import Repo


def reclone(repo_url, branch, work_dir):
    try:
        rmdir(work_dir)
    except FileNotFoundError:
        pass
    return Repo.clone_from(repo_url, work_dir, branch=branch)


def ensure_latest(repo_url, branch, work_dir):
    """If specified working directory contains a Git repo
    matching provided configuration (URL and branch), performs a pull.

    Otherwise, removes working directory if it exists
    and clones the repository afresh.

    :returns: Repo instance"""

    if all([path.isdir(work_dir),
            path.isdir(path.join(work_dir, '.git')),
            access(work_dir, R_OK)]):

        repo = Repo(work_dir)

        if all(['origin' in repo.remotes,
                repo.remotes.origin.url == repo_url,
                repo.active_branch.name == branch]):
            repo.remotes.origin.pull(no_rebase=True)

        else:
            repo = reclone(repo_url, branch, work_dir)

    else:
        repo = reclone(repo_url, branch, work_dir)

    return repo
