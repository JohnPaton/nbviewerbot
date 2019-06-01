"""Resources for nbvewerbot functionality"""

import os
import re
import logging
import pickle

import dotenv
import praw

# Relevant directories
SRC_DIR = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(SRC_DIR, "resources.d")
PROJECT_DIR = os.path.realpath(os.path.join(SRC_DIR, ".."))

# Logging
LOGFILE_PATH = os.path.join(PROJECT_DIR, "nbviewerbot.log")
LOGGER = logging.getLogger("nbviewerbot")

# Reddit auth info from PROJECT_DIR/.env
DOTENV_PATH = os.path.join(SRC_DIR, ".env")

dotenv.load_dotenv(DOTENV_PATH)


# Reddit authentication
def get_reddit_auth_kwargs():
    """Get the authentication kwargs for praw.Reddit from the environment.

    Requires the following environment variables to be set:
    * CLIENT_ID : the ID of your script application
    * CLIENT_SECRET : the secret of your script application
    * USERNAME : the username of your bot's Reddit account
    * PASSWORD : the password of your bot's Reddit account

    See https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example
    for more details.

    """
    kwargs = dict()
    kwargs["client_id"] = os.environ.get("CLIENT_ID")
    kwargs["client_secret"] = os.environ.get("CLIENT_SECRET")
    kwargs["username"] = os.environ.get("USERNAME")
    kwargs["password"] = os.environ.get("PASSWORD")
    kwargs["user_agent"] = "python:nbviewerbot:v0.1.0 (by /u/jd_paton)"

    for key, value in kwargs.items():
        if value is None:
            raise KeyError(
                "{} not found in environment variables. "
                "Have you filled in your .env file?".format(key.upper())
            )
    return kwargs


def load_reddit():
    """
    Get the authentication kwargs from the environment and authenticate with
    Reddit.


    Returns
    -------
    praw.Reddit : the authenticated Reddit client

    See also: utils.get_reddit_auth_kwargs
    """
    kwargs = get_reddit_auth_kwargs()
    reddit = praw.Reddit(**kwargs)
    LOGGER.info("Successfully authenticated with Reddit")
    return reddit


# Templates (for use with string.format)
NBVIEWER_URL_TEMPLATE = "https://nbviewer.jupyter.org/url/{}"

BINDER_URL_TEMPLATE_NO_FILEPATH = "https://mybinder.org/v2/gh/{}/{}"

BINDER_URL_TEMPLATE_WITH_FILEPATH = "https://mybinder.org/v2/gh/{}/{}?filepath={}"


_comment_footer = """

------

^(I am a bot.) 
[^(Feedback)](https://www.reddit.com/message/compose/?to=jd_paton) ^(|) 
[^(GitHub)](https://github.com/JohnPaton/nbviewerbot) ^(|) 
[^(Author)](https://johnpaton.net/)

"""

COMMENT_TEMPLATE_SINGLE = (
    """
I see you've posted a GitHub link to a Jupyter Notebook! GitHub doesn't 
render Jupyter Notebooks on mobile, so here is an 
[nbviewer](https://nbviewer.jupyter.org/) link to the notebook 
for mobile viewing:

{}

"""
    + _comment_footer
)

COMMENT_TEMPLATE_MULTI = (
    """
I see you've posted GitHub links to Jupyter Notebooks! GitHub doesn't 
render Jupyter Notebooks on mobile, so here are 
[nbviewer](https://nbviewer.jupyter.org/) links to the notebooks
for mobile viewing:

{}

"""
    + _comment_footer
)

# Regexes
_url_rx = "^http.*"
URL_RX = re.compile(_url_rx)

# Activity tracking
REPLY_DICT_PATH = os.path.join(SRC_DIR, "reply_dict.pkl")
try:
    with open(REPLY_DICT_PATH, "rb") as h:
        REPLY_DICT = pickle.load(h)
except FileNotFoundError:
    REPLY_DICT = {}

# Subreddit lists
SUBREDDITS_TEST = [
    "testingground4bots",
    "bottestingplace",
    "bottesting",
    "bottest",
]

SUBREDDITS_RELEVANT_PATH = os.path.join(RESOURCES_DIR, "subreddits.txt")
with open(SUBREDDITS_RELEVANT_PATH, "r") as h:
    _raw = h.readlines()
    # strip whitespace and drop empty lines
    SUBREDDITS_RELEVANT = [sub.strip() for sub in _raw]
    SUBREDDITS_RELEVANT = [sub for sub in SUBREDDITS_RELEVANT if sub]
    SUBREDDITS_RELEVANT += SUBREDDITS_TEST

SUBREDDITS_ALL = ["all"]
