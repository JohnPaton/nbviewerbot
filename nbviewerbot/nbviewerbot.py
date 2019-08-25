import logging
import atexit
from pprint import pformat
import multiprocessing.dummy as mp
import queue
import sys

import click
import backoff
import praw.exceptions
import praw.models
import prawcore.exceptions
import dotenv

from nbviewerbot import resources, utils, templating


# Exceptions that we will retry on
_PRAW_EXCEPTIONS = (
    praw.exceptions.PRAWException,
    prawcore.exceptions.PrawcoreException,
    prawcore.exceptions.ResponseException,
    prawcore.exceptions.RequestException,
)


def get_streams(subreddits):
    """Return the comment and submission streams for a subreddit or list of
    subreddit names"""
    if type(subreddits) is str:
        subreddits = [subreddits]

    reddit = resources.load_reddit()
    subreddit_str = "+".join(subreddits)
    sub = reddit.subreddit(subreddit_str)

    resources.LOGGER.info("Streaming comments from {}".format(subreddit_str))

    return sub.stream.comments(pause_after=0), sub.stream.submissions(pause_after=0)


@backoff.on_exception(
    backoff.expo,
    exception=_PRAW_EXCEPTIONS,
    max_tries=5,
    on_backoff=lambda x: resources.LOGGER.warning(
        "Exception replying to comment {}, sleeping. Details: {}".format(
            x["args"][0].id, str(x)
        )
    ),
    on_giveup=lambda x: resources.LOGGER.exception(
        "Max retries reached, giving up on comment {}. Details: {}".format(
            x["args"][0].id, str(x)
        )
    ),
)
def post_reply(praw_obj, text):
    """Reply to a comment or submisson with text. Will back off on
    PRAW exceptions.

    See also: templating.comment
    """
    reply = praw_obj.reply(text)
    obj_type = utils.praw_object_type(praw_obj)
    resources.LOGGER.info(
        "Replied to {} {} with new comment {}".format(obj_type, praw_obj.id, reply.id)
    )
    return reply


def process_praw_object(praw_obj):
    """Check a praw object for Jupyter GitHub links and reply if
    haven't already."""
    logger = resources.LOGGER
    obj_type = utils.praw_object_type(praw_obj)
    obj_id = praw_obj.id

    logger.debug("Processing {} {}".format(obj_type, obj_id))

    # don't reply to comments more than once
    if obj_id in resources.REPLY_DICT:
        logger.debug("Skipping {} {}, already replied".format(obj_type, obj_id))
        return

    jupy_links = []
    if isinstance(praw_obj, praw.models.Comment):
        jupy_links = utils.get_comment_jupyter_links(praw_obj)
    elif isinstance(praw_obj, praw.models.Submission):
        jupy_links = utils.get_submission_jupyter_links(praw_obj)

    if jupy_links:
        logger.info("Found Jupyter link(s) in {} {}".format(obj_type, obj_id))

        reply_text = templating.comment(jupy_links)

        # use function for posting comment to catch rate limit exceptions
        reply = post_reply(praw_obj, reply_text)

        resources.REPLY_DICT[obj_id] = reply


def main(subreddits):
    """
    Get comment stream for subreddits and process them. Will continue
    until interrupted.

    Parameters
    ----------
    subreddits : list[str]
        The subreddits to process comments from

    """

    logger = resources.LOGGER
    comments, submissions = get_streams(subreddits)
    main_queue = mp.Queue(1024)
    stop_event = mp.Event()  # for stopping workers

    # save the reply dict when the script exits
    atexit.register(lambda: logger.info("Exited nbviewerbot"))
    atexit.register(utils.pickle_reply_dict)

    # create workers to add praw objects to the queue
    workers = []
    comments_worker = mp.DummyProcess(
        name="CommentWorker",
        target=utils.load_queue,
        args=(main_queue, comments, stop_event),
    )
    workers.append(comments_worker)

    submissions_worker = mp.DummyProcess(
        name="SubmissionWorker",
        target=utils.load_queue,
        args=(main_queue, submissions, stop_event),
    )
    workers.append(submissions_worker)

    # make sure workers end on main thread end
    atexit.register(lambda e: e.set(), stop_event)

    # let's get it started in here
    [w.start() for w in workers]
    logger.info("Started nbviewerbot, listening for new comments...")

    while not stop_event.is_set():
        try:
            praw_obj = main_queue.get(timeout=1)
            process_praw_object(praw_obj)
        except queue.Empty:
            pass  # no problems, just nothing in the queue
        except:
            stop_event.set()
            logger.exception("Uncaught exception on object, skipping. Details:")
            raise

        if not all([w.is_alive() for w in workers]):
            stop_event.set()
            raise InterruptedError("Praw worker died unexpectedly")


# TODO: Add --detach option and status/kill commands for background running
@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Show DEBUG logs (always available at " + resources.LOGFILE_PATH + ")",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    default=False,
    help="Don't show any command line output",
)
@click.option(
    "--subreddit-set",
    "-s",
    default="relevant",
    type=click.Choice(["relevant", "test", "all"]),
    help='Set of subreddits to use. Options: "relevant" '
    "(default, relevant subreddits + bot test subs), "
    '"all" (/r/all), '
    ' or "test" (only bot testing subreddits). Use the '
    '"nbviewerbot subreddits" command to view the complete '
    "lists.",
)
@click.option(
    "--env",
    "-e",
    type=click.Path(exists=True, allow_dash=True, resolve_path=True),
    help="A custom .env file for loading environment variables. "
    "Relevant vars: CLIENT_ID, CLIENT_SECRET, USERNAME, "
    "PASSWORD.",
)
def cli(ctx, verbose, quiet, subreddit_set, env):
    """
    Run the nbviewerbot on the selected subreddit set.
    """
    # only run the main program if there are no subcommands being invoked
    if ctx.invoked_subcommand is None:
        # select subreddit set
        subs = resources.SUBREDDITS_RELEVANT
        if subreddit_set.lower() == "all":
            subs = resources.SUBREDDITS_ALL
        elif subreddit_set.lower() == "test":
            subs = resources.SUBREDDITS_TEST

        # choose log level
        if verbose:
            utils.setup_logger(logging.DEBUG)
        elif quiet:
            utils.setup_logger(None)
        else:
            utils.setup_logger(logging.INFO)

        if env:
            dotenv.load_dotenv(env, override=True)

        main(subs)


@cli.command("subreddits")
def show_subreddits():
    """Show subreddits used by the -s options"""
    msg_test = pformat(list(sorted(resources.SUBREDDITS_TEST)), compact=True)
    msg_relevant = pformat(list(sorted(resources.SUBREDDITS_RELEVANT)), compact=True)
    msg_all = pformat(list(sorted(resources.SUBREDDITS_ALL)), compact=True)

    click.echo("Subreddits followed by nbviewerbot -s options:")
    click.echo('"relevant":')
    click.echo(msg_relevant)
    click.echo('\n"test":')
    click.echo(msg_test)
    click.echo('\n"all":')
    click.echo(msg_all)


if __name__ == "__main__":
    cli()
