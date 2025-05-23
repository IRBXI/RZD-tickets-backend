import pytest
from app.util.url import build_url


class TestUrlBuilder:
    def test_no_existing_query_single_param(self):
        url = "http://example.com"
        params = {"key": "value"}
        expected = "http://example.com?key=value"
        assert build_url(url, **params) == expected

    def test_no_existing_query_multiple_params(self):
        url = "http://example.com"
        params = {"a": "1", "b": "2"}
        expected = "http://example.com?a=1&b=2"
        assert build_url(url, **params) == expected

    def test_existing_query_single_param(self):
        url = "http://example.com?existing=yes"
        params = {"new": "param"}
        expected = "http://example.com?existing=yes&new=param"
        assert build_url(url, **params) == expected

    def test_existing_query_multiple_params(self):
        url = "http://example.com?x=3"
        params = {"a": "1", "b": "2"}
        expected = "http://example.com?x=3&a=1&b=2"
        assert build_url(url, **params) == expected

    def test_existing_query_no_new_params(self):
        url = "http://example.com?existing=yes"
        expected = url
        assert build_url(url) == expected

    def test_no_params_without_existing_query_raises_error(self):
        url = "http://example.com"
        with pytest.raises(IndexError):
            build_url(url)

    def test_add_params_to_existing_multiple_query_params(self):
        url = "http://site.com?x=1&y=2"
        params = {"z": 3}
        expected = "http://site.com?x=1&y=2&z=3"
        assert build_url(url, **params) == expected
