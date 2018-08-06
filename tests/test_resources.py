from nbviewerbot import resources
import dotenv
import os
import pytest

TEST_DIR = os.path.join(os.path.dirname(__file__))
DOTENV_PATH = os.path.join(TEST_DIR, '.env_test')


class TestGetRedditAuthKwargs:
    def test_reads_environ(self):
        dotenv_path = DOTENV_PATH  # make local for output
        dotenv.load_dotenv(dotenv_path, override=True)

        kwargs = resources.get_reddit_auth_kwargs()

        assert kwargs['username'] == 'username'
        assert kwargs['password'] == 'password'
        assert kwargs['client_id'] == 'client_id'
        assert kwargs['client_secret'] == 'client_secret'

    def test_raises_if_missing(self):
        dotenv_path = DOTENV_PATH  # make local for output
        required_env_vars = ['USERNAME', 'PASSWORD',
                             'CLIENT_ID', 'CLIENT_SECRET']

        for key in required_env_vars:
            dotenv.load_dotenv(dotenv_path, override=True)
            os.environ.pop(key)

            with pytest.raises(KeyError):
                resources.get_reddit_auth_kwargs()


class TestSubredditsRelevant:
    def test_has_subs(self):
        assert len(resources.SUBREDDITS_RELEVANT) > 0

    def test_no_empty_strings(self):
        assert '' not in resources.SUBREDDITS_RELEVANT


def test_reply_dict():
    assert type(resources.REPLY_DICT) is dict
