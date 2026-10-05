from .hn import fetch_api_stories, fetch_html_stories
from .orchestrator import run_source


def run_once() -> dict[str, int]:
    html = run_source("hn_html", fetch_html_stories)
    api = run_source("hn_api", fetch_api_stories)
    return {
        "hn_html": len(html),
        "hn_api": len(api),
    }


if __name__ == "__main__":
    result = run_once()
    print(" ".join(f"{key}={value}" for key, value in result.items()))
