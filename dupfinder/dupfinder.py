#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from functools import partial
import os

__AUTHOR__ = 'Nuno Miguel Casteloa da Silva',
__EMAIL__ = 'NunoMCSilva@gmail.com',
__VERSION__ = '1.0.1'

NUM_BYTES = 1024


def get_filepaths(*dirpaths):   # -> list:
    """Return file paths for all files in given directory paths."""

    # test for non-existent paths
    for dirpath in dirpaths:
        if not os.path.exists(dirpath):
            raise ValueError("path {0} doesn't exist".format(dirpath))
        elif not os.path.isdir(dirpath):
            raise ValueError("path {0} isn't a directory".format(dirpath))

    # get all file paths
    fpaths = []
    for dirpath in dirpaths:
        for root, dirs, fnames in os.walk(dirpath):
            for fname in fnames:
                fpath = os.path.join(root, fname)
                fpaths.append(fpath)

    return fpaths


def groupby(filepaths, func=os.path.getsize):   # filepaths: list -> dict:
    """Return categories of file paths grouped by given function. Defaults to getsize."""

    categories = dict()

    for filepath in filepaths:
        result = func(filepath)
        if result not in categories:
            categories[result] = []

        categories[result].append(filepath)

    return categories


def read_num_bytes(filepath, num_bytes=NUM_BYTES):     # filepath: str -> bytes:
    """Read a maximum certain number of bytes from a file. Defaults to NUM BYTES."""

    with open(filepath, 'rb') as f:
        return f.read(NUM_BYTES)


def hash_file(filepath):    #: str -> str:
    """Return a sha256 file hash."""

    import hashlib
    m = hashlib.sha256()

    with open(filepath, 'rb') as f:
        for block in iter(partial(f.read, NUM_BYTES), b''):
            m.update(block)

    return m.hexdigest()


# TODO: this 3 phases can be refactored into a single function
def dupfinder_phase1(filepaths):    # -> dict:
    """Return group of filepaths grouped by size where group has more than 1 filepath."""

    groups_by_size = groupby(filepaths)
    groups = {size: group for size, group in groups_by_size.items() if len(group) > 1}
    return groups


def dupfinder_phase2(filepaths):    # -> dict:
    """Return group of filepaths grouped by first 1024 bytes where group has more than 1 filepath."""

    groups_by_first_num_bytes = groupby(filepaths, func=read_num_bytes)
    groups = {size: group for size, group in groups_by_first_num_bytes.items() if len(group) > 1}
    return groups


def dupfinder_phase3(filepaths):    # -> dict:
    """Return group of filepaths grouped by sha256 hash value where group has more than 1 filepath."""

    groups_by_sha256_hash = groupby(filepaths, func=hash_file)
    groups = {size: group for size, group in groups_by_sha256_hash.items() if len(group) > 1}
    return groups


def dupfinder(*dirpaths):   # -> dict:
    """Return group of repeated files grouped by size."""

    repeated = dict()

    filepaths = get_filepaths(*dirpaths)
    for size, group1 in dupfinder_phase1(filepaths).items():
        for first, group2 in dupfinder_phase2(group1).items():
            for hash_, group3 in dupfinder_phase3(group2).items():
                repeated[size] = sorted(group3)

    return repeated


def show_result(*dirpaths):
    """Show the group of repeated files grouped by size."""

    repeated = dupfinder(*dirpaths)

    for size in sorted(repeated.keys(), reverse=True):
        print('{0} byte(s)'.format(size))
        for filepath in repeated[size]:
            print(filepath)
        print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='DuplicateFinder', description='Find duplicate files')
    parser.add_argument('dirpath', nargs='+', help='path to directory to search duplicate files in')
    parser.add_argument('--version', action='version', version='%(prog)s {0}'.format(__VERSION__))
    args = parser.parse_args()
    show_result(*args.dirpath)
