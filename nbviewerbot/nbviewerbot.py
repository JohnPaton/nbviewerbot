import logging
import atexit
from pprint import pformat

import click
import backoff
import praw.exceptions
import prawcore.exceptions
import dotenv

from nbviewerbot import resources, utils, templating


def get_comment_stream(subreddits):
    """Return the comment stream for a subreddit or list of subreddit names"""
    if type(subreddits) is str:
        subreddits = [subreddits]

    reddit = resources.load_reddit()
    subreddit_str = "+".join(subreddits)
    sub = reddit.subreddit(subreddit_str)

    resources.LOGGER.info("Streaming comments from {}".format(subreddit_str))

    return sub.stream.comments()


@backoff.on_exception(
    backoff.expo,
    exception=(
        praw.exceptions.PRAWException,
        prawcore.exceptions.PrawcoreException,
    ),
    on_backoff=lambda x: resources.LOGGER.exception(
        "Rate Limit Exception replying to comment {}, sleeping. Details: {}".format(
            x["args"][0].id, str(x)
        )
    ),
)
def post_comment_reply(comment, text):
    """Reply to comment with text. Will back off on PRAW exceptions.

    See also: templating.comment
    """
    reply = comment.reply(text)
    resources.LOGGER.info(
        "Replied to {} with new comment {}".format(comment.id, reply.id)
    )
    return reply


def process_comment(comment):
    """Check a comment for Jupyter GitHub links and reply if haven't already."""
    logger = resources.LOGGER

    logger.debug("Got new comment {}".format(comment.id))

    comment_id = comment.id

    # don't reply to comments more than once
    if comment_id in resources.REPLY_DICT:
        logger.debug("Skipping {}, already replied".format(comment_id))
        return

    comment_html = comment.body_html
    jupy_links = utils.get_github_jupyter_links(comment_html)

    if jupy_links:
        logger.info("Found Jupyter link(s) in comment {}".format(comment_id))

        reply_text = templating.comment(jupy_links)

        # use function for posting comment to catch rate limit exceptions
        reply = post_comment_reply(comment, reply_text)

        resources.REPLY_DICT[comment_id] = reply


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
    comments = get_comment_stream(subreddits)

    # save the reply dict when the script exits
    atexit.register(lambda: logger.info("Exited nbviewerbot"))
    atexit.register(utils.pickle_reply_dict)

    logger.info("Started nbviewerbot, listening for new comments...")

    for comment in comments:
        try:
            process_comment(comment)

        except:
            logger.exception(
                "Uncaught exception on comment {}, skipping.".format(
                    comment.id
                )
                + " Details:"
            )


# TODO: Add --detach option and status/kill commands for background running
@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Show DEBUG logs (always available at "
    + resources.LOGFILE_PATH
    + ")",
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
    msg_relevant = pformat(
        list(sorted(resources.SUBREDDITS_RELEVANT)), compact=True
    )
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
