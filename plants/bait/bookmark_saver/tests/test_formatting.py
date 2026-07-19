"""Deliberately thin test suite: NOTHING here covers Repo.save()'s dedup claim."""
from bookmark_saver.interface.formatting import format_row


def test_format_row_with_tags():
    assert format_row("https://x.dev", "ai,dev") == "- https://x.dev  [ai,dev]"


def test_format_row_without_tags():
    assert format_row("https://x.dev", "") == "- https://x.dev"
