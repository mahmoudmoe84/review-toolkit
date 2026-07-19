"""Application services: the layer DESIGN.md says owns the validate() gate."""

from bookmark_saver.storage.repo import Repo

_repo = Repo("bookmarks.db")


def add_bookmark(url: str, tags: str) -> None:
    _repo.save(url, tags)


def list_bookmarks() -> list[tuple[str, str]]:
    return _repo.all_rows()
