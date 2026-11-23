"""Filter URLs to supported sites + optional web search."""
import os
import time
from urllib.parse import urlparse

import httpx

from .sites import domain_from_url


MONID_API = "https://api.monid.ai"


def filter_urls(urls: list[str], supported_domains: set[str]) -> list[dict]:
    """Filter a list of URLs to only those on supported paywall sites."""
    results = []
    seen = set()
    for url in urls:
        if url in seen:
            continue
        domain = domain_from_url(url)
        if domain in supported_domains:
            seen.add(url)
            results.append({"url": url, "domain": domain, "supported": True})
    return results


def search_brave(
    query: str,
    supported_domains: set[str],
    limit: int = 20,
    site_filter: str | None = None,
) -> list[dict]:
    """Search via Brave Search API. Requires BRAVE_API_KEY env var."""
    api_key = os.environ.get("BRAVE_API_KEY", "")
    if not api_key:
        return []
    search_query = f"site:{site_filter} {query}" if site_filter else query
    results: list[dict] = []
    try:
        resp = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": search_query, "count": min(limit * 2, 20)},
            headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
            timeout=15.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("web", {}).get("results", []):
                url = item.get("url", "")
                domain = domain_from_url(url)
                if site_filter:
                    if domain == site_filter or domain.endswith(f".{site_filter}"):
                        results.append(_format(item, domain))
                elif domain in supported_domains:
                    results.append(_format(item, domain))
                if len(results) >= limit:
                    break
    except Exception:
        pass
    return results[:limit]


def search_sites(
    query: str,
    supported_domains: set[str],
    limit: int = 20,
    site_filter: str | None = None,
) -> list[dict]:
    """Search supported sites using Monid or Brave Search."""
    if api_key := os.environ.get("MONID_API_KEY"):
        return _search_monid(api_key, query, supported_domains, limit, site_filter)
    return search_brave(query, supported_domains, limit, site_filter)


def _search_monid(
    api_key: str,
    query: str,
    supported_domains: set[str],
    limit: int,
    site_filter: str | None,
) -> list[dict]:
    search_query = f"site:{site_filter} {query}" if site_filter else query
    headers = {"Authorization": f"Bearer {api_key}"}
    results: list[dict] = []
    try:
        resp = httpx.post(
            f"{MONID_API}/v1/run",
            json={
                "provider": "search1api",
                "endpoint": "/search",
                "input": {"body": {"query": search_query, "max_results": max(1, min(limit * 2, 20))}},
            },
            headers=headers,
            timeout=15.0,
        )
        resp.raise_for_status()
        run = resp.json()
        if resp.status_code == 202:
            run_id = run["runId"]
            for _ in range(60):
                time.sleep(2)
                poll = httpx.get(f"{MONID_API}/v1/runs/{run_id}", headers=headers, timeout=15.0)
                poll.raise_for_status()
                run = poll.json()
                if run.get("status") in {"COMPLETED", "FAILED", "TIMED_OUT", "STOPPED", "BLOCKED"}:
                    break
            if run.get("status") != "COMPLETED":
                return []
        if (run.get("providerResponse") or {}).get("httpStatus", 200) >= 400:
            return []
        for item in run["output"].get("results", []):
            domain = domain_from_url(item.get("link", ""))
            if site_filter:
                match = domain == site_filter or domain.endswith(f".{site_filter}")
            else:
                match = domain in supported_domains
            if match:
                results.append(_format_monid(item, domain))
            if len(results) >= limit:
                break
    except Exception:
        pass
    return results[:limit]


def _format_monid(item: dict, domain: str) -> dict:
    return {
        "title": item.get("title", ""),
        "url": item.get("link", ""),
        "domain": domain,
        "snippet": item.get("snippet", ""),
    }


def _format(item: dict, domain: str) -> dict:
    return {
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "domain": domain,
        "snippet": item.get("description", ""),
    }
