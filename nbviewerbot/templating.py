import urllib

from nbviewerbot import utils, resources


def nbviewer_url(url):
    """Return the nbviewer url for the given url."""
    link = utils.get_notebook_path(url)
    return resources.NBVIEWER_URL_TEMPLATE.format(link)


def binder_url(repo, branch="master", filepath=None):
    """
    Build a binder url. If filepath is provided, the url will be for
    the specific file.

    Parameters
    ----------
    repo: str
        The repository in the form "username/reponame"
    branch: str, optional
        The branch, default "master"
    filepath: str, optional
        The path to a file in the repo, e.g. dir1/dir2/notebook.ipynb

    Returns
    -------
    str
        A binder url that will launch a notebook server
    """

    if filepath is not None:
        fpath = urllib.parse.quote(filepath, safe="")
        return resources.BINDER_URL_TEMPLATE_WITH_FILEPATH.format(
            repo, branch, filepath
        )

    else:
        return resources.BINDER_URL_TEMPLATE_NO_FILEPATH.format(repo, branch)


def comment_single_link(url):
    """Construct the single link bot reply comment for the given url"""
    link = nbviewer_url(url)
    return resources.COMMENT_TEMPLATE_SINGLE.format(link)


def comment_multi_link(urls):
    """Construct the multi-link bot comment reply for the given list of urls"""
    links = [nbviewer_url(url) for url in urls]
    links_string = "\n\n".join(links)
    return resources.COMMENT_TEMPLATE_MULTI.format(links_string)


def comment(urls):
    """
    Construct the bot comment reply for the given url or list of urls.

    If urls is a string or a list containing a single string, construct
    the single link reply. If urls is a list containing multiple
    strings, construct the multi-link reply.

    See resources.COMMENT_TEMPLATE_MULTI and
    resources.COMMENT_TEMPLATE_SINGLE.

    Parameters
    ----------
    urls : string or list of strings
        The url(s) to use in the comment

    Returns
    -------
    string : the constructed comment
    """
    if type(urls) is str:
        return comment_single_link(urls)

    elif len(urls) == 1:
        return comment_single_link(urls[0])

    else:
        return comment_multi_link(urls)
