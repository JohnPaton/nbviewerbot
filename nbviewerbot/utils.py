import urllib
import logging
import pickle

from bs4 import BeautifulSoup

from nbviewerbot import resources


def parse_url_if_not_parsed(url):
    """
    Return the urllib.parse.ParseResult for URL if it is not already parsed.

    Parameters
    ----------
    url : str or urllib.parse.ParseResult

    Returns
    -------
    urllib.parse.ParseResult : The parsed URL
    """
    if type(url) is urllib.parse.ParseResult:
        return url
    else:
        return urllib.parse.urlparse(url)


def is_github_jupyter_url(url):
    """
    Test if a url is a github jupyter url

    Parameters
    ----------
    url : str or urllib.parse.ParseResult

    Returns
    -------
    True if the host is 'github' and the path contains '.ipynb',
    else False
    """
    parsed = parse_url_if_not_parsed(url)

    return "github" in parsed.netloc.lower() and ".ipynb" in parsed.path.lower()


def get_notebook_path(url):
    """
    Convert a full URL into a path. Removes http(s):// and www. if present.

    Parameters
    ----------
    url : str or urllib.parse.ParseResult

    Returns
    -------
    str : the path

    Examples
    --------
    >>> nbviewerbot.utils.get_notebook_path(
    ...     'https://www.github.com/JohnPaton/numpy-neural-networks/blob/'
    ...     'master/01-single-layer-perceptron.ipynb'
    ... )
    'github.com/JohnPaton/numpy-neural-networks/blob/master/01-single-layer-perceptron.ipynb'

    """
    parsed = parse_url_if_not_parsed(url)
    return parsed.netloc.replace("www.", "") + parsed.path


def get_github_info(url):
    """
    Get the repo, branch and (optional) filepath from a github url

    Parameters
    ----------
    url

    Returns
    -------
    repo, branch, filepath (if present)
    """
    parsed = parse_url_if_not_parsed(url)
    assert "github" in parsed.netloc.lower(), "Must be a github url"
    assert len(parsed.path.split("/")) >= 3, "Must be at least a path to a repo"

    path_elements = parsed.path.split("/")  # drop the first slash

    repo = "/".join(path_elements[1:3])
    branch = "master"
    filepath = None

    if len(path_elements) >= 5:
        branch = path_elements[4]
    if len(path_elements) >= 6:
        filepath = "/".join(path_elements[5:])

    return repo, branch, filepath


def get_all_links(html):
    """
    Parse HTML and extract all http(s) hyperlink destinations

    Parameters
    ----------
    html : str

    Returns
    -------
    list[str] : the found URLs (if any)

    """
    soup = BeautifulSoup(html, features="html.parser")
    links = soup.find_all("a", attrs={"href": resources.URL_RX})
    return [link.get("href") for link in links]


def get_github_jupyter_links(html):
    """
    Parse HTML and exract all links to Jupyter Notebooks hosted on GitHub

    Parameters
    ----------
    html : str

    Returns
    -------
    list[str] : the found URLs (if any)

    See also: utils.is_github_jupyter_url
    """
    links = get_all_links(html)
    return [link for link in links if is_github_jupyter_url(link)]


def get_comment_jupyter_links(comment):
    """Extract jupyter lins from a comment, if any"""
    html = comment.body_html
    jupy_links = get_github_jupyter_links(html)
    return jupy_links


def get_submission_jupyter_links(submission):
    """Extract jupyer links from a submission, if any"""
    jupy_links = []
    if submission.selftext_html is not None:
        # self post, read html
        html = submission.selftext_html
        jupy_links += get_github_jupyter_links(html)

    if is_github_jupyter_url(submission.url):
        jupy_links += [submission.url]

    # dedupe
    jupy_links = list(dict.fromkeys(jupy_links))

    return jupy_links


def setup_logger(console_level=logging.INFO, file_level=logging.DEBUG):
    """
    Set up the nbviewerbot with a level for console logging and a level for
    file logging. If either level is None, do not log to that destination.

    Parameters
    ----------
    console_level : int or None
        The log level for the console

    file_level : int or None
        The log level for the file

    Returns
    -------
    logger
    """
    logger = logging.getLogger("nbviewerbot")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s %(levelname)s(%(threadName)s) - %(message)s")

    if console_level is not None:
        sh = logging.StreamHandler()
        sh.setLevel(console_level)
        sh.setFormatter(fmt)
        logger.addHandler(sh)

    if file_level is not None:
        fh = logging.FileHandler(resources.LOGFILE_PATH)
        fh.setLevel(file_level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


def pickle_reply_dict():
    """
    Pickle resources.REPLY_DICT to resources.REPLY_DICT_PATH.
    """
    resources.LOGGER.info("Saving reply log...")
    with open(resources.REPLY_DICT_PATH, "wb") as h:
        pickle.dump(resources.REPLY_DICT, h)


def praw_object_type(praw_obj):
    """Return the type of the praw object (comment/submission) as a
    lowercase string."""
    return type(praw_obj).__name__.lower()


def raise_on_exception(e):
    """Raises exception e"""
    raise e


def load_queue(queue, iterable, stop_event=None):
    """Put items from iterable into queue as they become available

    Stops when stop_event is set if provided, else continues forever.
    """
    for i in iterable:
        queue.put(i)
        resources.LOGGER.debug("Queued item {}".format(i))
        if stop_event.is_set():
            resources.LOGGER.info("Stop signal received, stopping")
            break
