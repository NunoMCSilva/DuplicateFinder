#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: needs some refactoring

import pytest
import os
from .capturing import Capturing
import dupfinder


@pytest.fixture(scope='session')
def directory(tmpdir_factory):
    """Create test directory and files."""

    # create test directory and files
    dirs = list()
    files = list()
    for i in range(3):
        d = tmpdir_factory.mktemp('dir{0}'.format(i))
        dirs.append(d)
        for j in range(3):
            f = d.join('file{0}{1}.txt'.format(i, j))
            files.append(f)

    # fill files
    # 1024 bytes
    files[0].write('a' * 1024)                  # 2edc986847e209b4016e141a6dc8716d3207350f416969382d431539bf292e4a
    files[1].write('a' * 1024)                  # 2edc986847e209b4016e141a6dc8716d3207350f416969382d431539bf292e4a
    files[2].write('b' * 1024)                  # 0c66f2c45405de575189209a768399bcaf88ccc51002407e395c0136aad2844d

    # 2048 bytes
    files[3].write('a' * 2048)                  # b2a3a502fdfc34f4e3edfa94b7f3109cd972d87a4fec63ab21a6673379ccf7ad
    files[4].write('a' * 2048)                  # b2a3a502fdfc34f4e3edfa94b7f3109cd972d87a4fec63ab21a6673379ccf7ad
    files[5].write('a' * 1024 + 'b' * 1024)     # d649296e80910172162d1c63a1f82bfc6dd13d2ca9cbf33cc5eb298a9d19a454

    # 2048 bytes
    files[6].write('c' * 2048)                  # 71899db2707c5d7dc62d01bcf923431418374e9fb42a3fcb6d83e5cc017c2173
    # files[7].write('c' * 2048)                  # 71899db2707c5d7dc62d01bcf923431418374e9fb42a3fcb6d83e5cc017c2173
    files[7].write('d' * 2048)                  # 8b2b19289efc06a17436f0eba6ff47737a490560b97f96a9478a942bf41fa399

    # 3072 bytes
    files[8].write('e' * (1024 * 3))            # c307ea816b283f15fe85975fe848908adc52db13f512e2d9407ea8a14baf5c10

    return tmpdir_factory


def test_get_filepaths_returns_correct(directory):
    dirpath = directory.getbasetemp().strpath

    expected = ['dir00/file00.txt', 'dir00/file01.txt', 'dir00/file02.txt',
                'dir10/file10.txt', 'dir10/file11.txt', 'dir10/file12.txt',
                'dir20/file20.txt', 'dir20/file21.txt', 'dir20/file22.txt']
    expected = [os.path.join(dirpath, dpath) for dpath in expected]

    listdir = [os.path.join(dirpath, d) for d in os.listdir(dirpath) if d != '.lock']
    assert sorted(dupfinder.get_filepaths(*listdir)) == expected


def test_get_filepaths_non_existent_dirpath_raises_error(directory):
    dirpath = directory.getbasetemp().strpath

    listdir = [os.path.join(dirpath, d) for d in os.listdir(dirpath) if d != '.lock']
    listdir.append('dir30')

    with pytest.raises(ValueError):
        dupfinder.get_filepaths(*listdir)


def test_get_filepaths_not_dir_dirpath_raises_error(directory):
    dirpath = directory.getbasetemp().strpath

    listdir = [os.path.join(dirpath, d) for d in os.listdir(dirpath) if d != '.lock']
    listdir.append(os.path.join(dirpath, 'dir00/file00.txt'))

    with pytest.raises(ValueError):
        dupfinder.get_filepaths(*listdir)


def test_categorize_getsize_returns_correct(directory):
    dirpath = directory.getbasetemp().strpath

    expected = {1024: ['dir00/file00.txt', 'dir00/file01.txt', 'dir00/file02.txt'],
                2048: ['dir10/file10.txt', 'dir10/file11.txt', 'dir10/file12.txt',
                       'dir20/file20.txt', 'dir20/file21.txt'],
                3072: ['dir20/file22.txt']}

    expected[1024] = [os.path.join(dirpath, dpath) for dpath in expected[1024]]
    expected[2048] = [os.path.join(dirpath, dpath) for dpath in expected[2048]]
    expected[3072] = [os.path.join(dirpath, dpath) for dpath in expected[3072]]

    filepaths = [f for f in dupfinder.get_filepaths(dirpath) if not f.endswith('.lock')]
    assert dupfinder.groupby(sorted(filepaths)) == expected


@pytest.mark.parametrize('file,expected', [
    [b'a' * dupfinder.NUM_BYTES + b'b', b'a' * dupfinder.NUM_BYTES],
    [b'ab', b'ab']
])
def test_read_num_bytes_returns_correct(file, expected, tmpdir):
    f = tmpdir.join('file.txt')
    f.write(file)

    assert dupfinder.read_num_bytes(f.strpath) == expected


# this this better -- size
def test_hash_file(tmpdir):
    f = tmpdir.join('file.txt')
    f.write('abcde' * 1024)

    assert dupfinder.hash_file(f.strpath) == '648162bb4ea285046f959de0785e86053a0fb004d3a5fb615351bc5bdb11c067'


def test_dupfinder_phase1(directory):
    dirpath = directory.getbasetemp().strpath

    expected = {1024: ['dir00/file00.txt', 'dir00/file01.txt', 'dir00/file02.txt'],
                2048: ['dir10/file10.txt', 'dir10/file11.txt', 'dir10/file12.txt',
                       'dir20/file20.txt', 'dir20/file21.txt']}

    expected[1024] = [os.path.join(dirpath, dpath) for dpath in expected[1024]]
    expected[2048] = [os.path.join(dirpath, dpath) for dpath in expected[2048]]

    filepaths = [f for f in dupfinder.get_filepaths(dirpath) if not f.endswith('.lock')]
    assert dupfinder.dupfinder_phase1(sorted(filepaths)) == expected


def test_dupfinder_phase2(directory):
    dirpath = directory.getbasetemp().strpath

    expected1024 = dict()
    expected1024[b'a' * 1024] = ['dir00/file00.txt', 'dir00/file01.txt']

    expected2048 = dict()
    expected2048[b'a' * 1024] = ['dir10/file10.txt', 'dir10/file11.txt', 'dir10/file12.txt']

    expected1024 = {k: [os.path.join(dirpath, vi) for vi in v] for k, v in expected1024.items()}
    expected2048 = {k: [os.path.join(dirpath, vi) for vi in v] for k, v in expected2048.items()}

    filepaths = [f for f in dupfinder.get_filepaths(dirpath) if not f.endswith('.lock')]
    groups = dupfinder.dupfinder_phase1(sorted(filepaths))

    for size, group in groups.items():
        if size == 1024:
            assert dupfinder.dupfinder_phase2(group) == expected1024
        elif size == 2048:
            assert dupfinder.dupfinder_phase2(group) == expected2048


def test_dupfinder_phase3(directory):
    dirpath = directory.getbasetemp().strpath

    expected1024 = dict()
    expected1024['2edc986847e209b4016e141a6dc8716d3207350f416969382d431539bf292e4a'] = ['dir00/file00.txt',
                                                                                        'dir00/file01.txt']
    expected2048 = dict()
    expected2048['b2a3a502fdfc34f4e3edfa94b7f3109cd972d87a4fec63ab21a6673379ccf7ad'] = ['dir10/file10.txt',
                                                                                        'dir10/file11.txt']

    expected1024 = {k: [os.path.join(dirpath, vi) for vi in v] for k, v in expected1024.items()}
    expected2048 = {k: [os.path.join(dirpath, vi) for vi in v] for k, v in expected2048.items()}

    filepaths = [f for f in dupfinder.get_filepaths(dirpath) if not f.endswith('.lock')]

    groups = dupfinder.dupfinder_phase1(sorted(filepaths))
    for size, group in groups.items():
        if size == 1024:
            groups1024 = dupfinder.dupfinder_phase2(group)
            for first, group1 in groups1024.items():
                assert dupfinder.dupfinder_phase3(group1) == expected1024

        if size == 2048:
            groups2048 = dupfinder.dupfinder_phase2(group)
            for first, group2 in groups2048.items():
                assert dupfinder.dupfinder_phase3(group2) == expected2048


def test_dupfinder(directory):
    dirpath = directory.getbasetemp().strpath

    expected1024 = dict()
    expected1024['2edc986847e209b4016e141a6dc8716d3207350f416969382d431539bf292e4a'] = ['dir00/file00.txt',
                                                                                        'dir00/file01.txt']
    expected2048 = dict()
    expected2048['b2a3a502fdfc34f4e3edfa94b7f3109cd972d87a4fec63ab21a6673379ccf7ad'] = ['dir10/file10.txt',
                                                                                        'dir10/file11.txt']

    expected1024 = {k: [os.path.join(dirpath, vi) for vi in v] for k, v in expected1024.items()}
    expected2048 = {k: [os.path.join(dirpath, vi) for vi in v] for k, v in expected2048.items()}

    # expected = [list(expected1024.values())[0], list(expected2048.values())[0]]
    expected = {1024: list(expected1024.values())[0], 2048: list(expected2048.values())[0]}

    listdir = [os.path.join(dirpath, d) for d in os.listdir(dirpath) if d != '.lock']
    assert dupfinder.dupfinder(*listdir) == expected


def test_show_results(directory):
    dirpath = directory.getbasetemp().strpath
    listdir = [os.path.join(dirpath, d) for d in os.listdir(dirpath) if d != '.lock']

    with Capturing() as output:
        dupfinder.show_result(*listdir)

    assert output == ['2048 byte(s)',
                      os.path.join(dirpath, 'dir10/file10.txt'),
                      os.path.join(dirpath, 'dir10/file11.txt'),
                      '',
                      '1024 byte(s)',
                      os.path.join(dirpath, 'dir00/file00.txt'),
                      os.path.join(dirpath, 'dir00/file01.txt'),
                      '']
