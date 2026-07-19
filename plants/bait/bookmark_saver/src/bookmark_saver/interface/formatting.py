"""Row formatting helpers for CLI output."""


def format_row(url: str, tags: str) -> str:
    tag_part = f"  [{tags}]" if tags else ""
    return f"- {url}{tag_part}"
