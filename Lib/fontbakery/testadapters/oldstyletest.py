# -*- coding: utf-8 -*-
"""
Font Bakery OldStyleTest is a wrapper to make it easier to port
old style fontbakery/checks tests to TestRunner.
It's no complete drop-in replacement, but it hopefully can speed up our
transition to the new runner style.
Don't use this for any other purpose. This is an interim solution and
will be deprecated in the future.
"""
from __future__ import absolute_import, print_function, unicode_literals

from collections import namedtuple
from functools import partial, wraps
from fontbakery.testrunner import SKIP, PASS, INFO, WARN, FAIL
from fontbakery.callable import FontBakeryTest


_FbloggerAPI = namedtuple('FblogAPI',
                       ['skip', 'ok', 'info', 'warning', 'error'])

def _initFbloggerAPI():
    results = []
    def report(status, message):
        results.append((status, message))
    fb = _FbloggerAPI(*[partial(report, status)
                        for status in (SKIP, PASS, INFO, WARN, FAIL)])
    return fb, results

def _gen(results):
    # creates a generator, which we understand
    # in TestRunner._exec_test
    for result in results:
        yield result

class OldStyleTest(FontBakeryTest):
    def __init__(oldstyletest, id, *args, **kwargs):
        # we'll inspect the arguments directly from oldstyletest
        super(OldStyleTest, OldStyleTest).__init__(oldstyletest, id,
                                                        *args, **kwargs)

    _ignore_mandatory_args = {'fb'}

    def __call__(self, *args, **kwargs):
        fb, results = _initFbloggerAPI()
        try:
            self._func(fb, *args, **kwargs)
        except Exception as e:
            results.append((FAIL, e))

        return _gen(results)

def oldStyleTest(id, *args, **kwds):
    def wrapper(func):
        return wraps(func)(
                OldStyleTest(func, id, *args, **kwds))
    return wrapper