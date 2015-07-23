from __future__ import unicode_literals

from posixps import sub


def test_no_subs():
    assert(sub("hello world") == "hello world")


def test_simple_sub():
    assert(sub("hello ${thing}", thing="world") == "hello world")
