import pytest
from urllib.parse import urlparse
from nbviewerbot import utils


class TestParseUrlIfNotParsed:
    def test_not_parsed(self):
        url = "https://github.com"
        parsed = utils.parse_url_if_not_parsed(url)
        assert parsed == urlparse(url)

    def test_parsed(self):
        url = urlparse("https://github.com")
        parsed = utils.parse_url_if_not_parsed(url)
        assert parsed == url


class TestIsGithubJupyterUrl:
    def test_both(self):
        url = "https://github.com/username/repo/test.ipynb"
        assert utils.is_github_jupyter_url(url)
        assert utils.is_github_jupyter_url(urlparse(url))

    def test_github(self):
        url = "http://github.com"
        assert not utils.is_github_jupyter_url(url)
        assert not utils.is_github_jupyter_url(urlparse(url))

    def test_jupyter(self):
        url = "www.example.com/test.ipynb"
        assert not utils.is_github_jupyter_url(url)
        assert not utils.is_github_jupyter_url(urlparse(url))

    def test_neither(self):
        url = "http://google.com"
        assert not utils.is_github_jupyter_url(url)
        assert not utils.is_github_jupyter_url(urlparse(url))


class TestGetNotebookPath:
    def test_normal(self):
        url = "https://github.com/username/repo/test.ipynb"
        expected = "github.com/username/repo/test.ipynb"
        assert utils.get_notebook_path(url) == expected
        assert utils.get_notebook_path(urlparse(url)) == expected

    def test_www(self):
        url = "http://www.github.com/username/repo/test.ipynb"
        expected = "github.com/username/repo/test.ipynb"
        assert utils.get_notebook_path(url) == expected
        assert utils.get_notebook_path(urlparse(url)) == expected

    def test_params(self):
        url = "https://github.com/username/repo/test.ipynb?param=on"
        expected = "github.com/username/repo/test.ipynb"
        assert utils.get_notebook_path(url) == expected
        assert utils.get_notebook_path(urlparse(url)) == expected

    def test_hash(self):
        url = "https://github.com/username/repo/test.ipynb#section1"
        expected = "github.com/username/repo/test.ipynb"
        assert utils.get_notebook_path(url) == expected
        assert utils.get_notebook_path(urlparse(url)) == expected


class TestGetAllLinks:
    def test_no_links(self):
        html = "this isn't even html"
        links = utils.get_all_links(html)
        assert links == []

    def test_links(self):
        html = "some text <a href=http://www.example.com> also" " <a href=http://www.github.com>"
        links = utils.get_all_links(html)
        expected = ["http://www.example.com", "http://www.github.com"]
        assert links == expected

    def test_hash(self):
        html = "some text <a href=http://www.example.com> also" " <a href=#secion1>"
        links = utils.get_all_links(html)
        expected = ["http://www.example.com"]
        assert links == expected


class TestGetGithubJupyterLinks:
    def test_no_links(self):
        html = "this isn't even html"
        links = utils.get_github_jupyter_links(html)
        assert links == []

    def test_links(self):
        html = "some text <a href=http://www.example.com> also" " <a href=http://www.github.com/username/repo/test.ipynb>"
        links = utils.get_github_jupyter_links(html)
        expected = ["http://www.github.com/username/repo/test.ipynb"]
        assert links == expected

    def test_hash(self):
        html = "some text " "<a href=http://www.github.com/username/repo/test.ipynb> also" " <a href=#secion1>"
        links = utils.get_github_jupyter_links(html)
        expected = ["http://www.github.com/username/repo/test.ipynb"]
        assert links == expected

    def test_other_links(self):
        html = "some text <a href=http://www.example.com> also" " <a href=http://www.github.com>"
        links = utils.get_github_jupyter_links(html)
        assert links == []
