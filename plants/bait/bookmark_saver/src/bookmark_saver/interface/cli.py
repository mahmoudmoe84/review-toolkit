"""CLI entry point."""
import argparse

from bookmark_saver.application.service import add_bookmark, list_bookmarks
from bookmark_saver.interface.formatting import format_row


def main() -> None:
    parser = argparse.ArgumentParser(prog="bm")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("url")
    p_add.add_argument("--tags", default="")

    sub.add_parser("list")

    args = parser.parse_args()
    if args.cmd == "add":
        # NOTE: url goes straight to the service; service forwards to storage.
        add_bookmark(args.url, args.tags)
        print("saved.")
    elif args.cmd == "list":
        for url, tags in list_bookmarks():
            print(format_row(url, tags))


if __name__ == "__main__":
    main()
