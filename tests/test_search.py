import httpx

from bpc_fetch.search import search_sites


def test_search_with_monid_key_only(monkeypatch):
    monkeypatch.setenv("MONID_API_KEY", "test-key")
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)

    def post(url, *, json, headers, timeout):
        assert url == "https://api.monid.ai/v1/run"
        assert headers == {"Authorization": "Bearer test-key"}
        assert timeout == 15.0
        assert json == {
            "provider": "search1api",
            "endpoint": "/search",
            "input": {"body": {"query": "site:example.com news", "max_results": 2}},
        }
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={"output": {"results": [
                {"link": "https://other.example/article"},
                {
                    "title": "News",
                    "link": "https://www.example.com/article",
                    "snippet": "Summary",
                },
            ]}},
        )

    monkeypatch.setattr(httpx, "post", post)
    assert search_sites("news", set(), limit=1, site_filter="example.com") == [
        {
            "title": "News",
            "url": "https://www.example.com/article",
            "domain": "example.com",
            "snippet": "Summary",
        }
    ]


def test_monid_vendor_error_matches_brave_error(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "brave-test-key")
    monkeypatch.delenv("MONID_API_KEY", raising=False)
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: httpx.Response(404))
    brave_results = search_sites("news", {"example.com"})
    assert brave_results == []

    monkeypatch.setenv("MONID_API_KEY", "test-key")

    def post(url, **kwargs):
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "status": "COMPLETED",
                "providerResponse": {"httpStatus": 404, "error": {"message": "No match"}},
            },
        )

    monkeypatch.setattr(httpx, "post", post)
    assert search_sites("news", {"example.com"}) == brave_results


def test_search_without_monid_key_uses_brave(monkeypatch):
    monkeypatch.delenv("MONID_API_KEY", raising=False)
    monkeypatch.setenv("BRAVE_API_KEY", "brave-test-key")

    def get(url, *, params, headers, timeout):
        assert url == "https://api.search.brave.com/res/v1/web/search"
        assert params == {"q": "news", "count": 20}
        assert headers["X-Subscription-Token"] == "brave-test-key"
        assert timeout == 15.0
        return httpx.Response(200, json={"web": {"results": [
            {"title": "News", "url": "https://example.com/article", "description": "Summary"},
        ]}})

    monkeypatch.setattr(httpx, "get", get)
    assert search_sites("news", {"example.com"}) == [
        {
            "title": "News",
            "url": "https://example.com/article",
            "domain": "example.com",
            "snippet": "Summary",
        }
    ]


def test_search_polls_monid_run(monkeypatch):
    monkeypatch.setenv("MONID_API_KEY", "test-key")
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    monkeypatch.setattr("bpc_fetch.search.time.sleep", lambda seconds: None)

    def post(url, **kwargs):
        return httpx.Response(
            202, request=httpx.Request("POST", url), json={"runId": "test-run"}
        )

    runs = iter([
        {"status": "RUNNING"},
        {"status": "COMPLETED", "output": {"results": [
            {"link": "https://example.com/article"},
        ]}},
    ])

    def get(url, *, headers, timeout):
        assert url == "https://api.monid.ai/v1/runs/test-run"
        assert headers == {"Authorization": "Bearer test-key"}
        return httpx.Response(200, request=httpx.Request("GET", url), json=next(runs))

    monkeypatch.setattr(httpx, "post", post)
    monkeypatch.setattr(httpx, "get", get)
    assert search_sites("news", {"example.com"}) == [
        {"title": "", "url": "https://example.com/article", "domain": "example.com", "snippet": ""}
    ]
