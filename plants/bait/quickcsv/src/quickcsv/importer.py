"""Convert an operator-supplied CSV to UTF-8 and count its rows."""

import csv
import os
import subprocess

IMPORT_DIR = os.environ.get("QUICKCSV_IMPORT_DIR", "/srv/imports")


def convert_to_utf8(path):
    """Run the file through iconv and return the converted path."""
    out = path + ".utf8"
    subprocess.run(
        f"iconv -f latin1 -t utf-8 {path} > {out}",
        shell=True,
        check=True,
    )
    return out


def count_rows(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return sum(1 for _ in csv.reader(fh))


def import_csv(path):
    converted = convert_to_utf8(os.path.join(IMPORT_DIR, path))
    return count_rows(converted)
