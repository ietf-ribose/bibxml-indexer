from django.conf import settings


GITHUB_REPO_URL = "git://github.com/{user}/{repo}.git"


def locate_bibxml_source_repo(dataset_id):
    """
    :param dataset_id: dataset ID as string
    :returns: tuple (repo_url, repo_branch)
    """
    overrides = ((settings.DATASET_SOURCE_OVERRIDES or {}).
                 get(dataset_id, {}).
                 get('bibxml_data', {}))
    return (
      overrides.get(
        'repo_url',
        GITHUB_REPO_URL.format(
          user='ietf-ribose',
          repo='bibxml-data-%s' % dataset_id)),
      overrides.get('repo_branch', 'main'),
    )


def locate_relaton_source_repo(dataset_id):
    """
    .. note:: Deprecated when ``relaton-bib-py`` is used to generate Relaton data instead.

    :param dataset_id: dataset ID as string
    :returns: tuple (repo_url, repo_branch)
    """
    overrides = ((settings.DATASET_SOURCE_OVERRIDES or {}).
                 get(dataset_id, {}).
                 get('relaton_data', {}))

    return (
      overrides.get(
        'repo_url',
        GITHUB_REPO_URL.format(
          user='relaton',
          repo='relaton-data-%s' % dataset_id)),
      overrides.get('repo_branch', 'master'),
    )
