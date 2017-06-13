#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from https://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call

from io import StringIO
import sys


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._string_io = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._string_io.getvalue().splitlines())
        del self._string_io  # free up some memory
        sys.stdout = self._stdout
