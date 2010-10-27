from textwrap import dedent

from nose.tools import assert_equal, raises, assert_false, assert_true

from datadiff import diff

from pprint import pformat
from unittest import TestCase
import nose
from nose.config import Config


@raises(Exception)
def test_diff_objects():
    class Foo(object): pass
    diff(Foo(), Foo())

def test_diff_list():
    a = [1,'x', 2, 3, 4, 5]
    b = [1,'y', 2, 4, 6]
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        @@ @@
        [
         1,
        -'x',
        +'y',
         2,
        -3,
         4,
        -5,
        +6,
        ]''')
    print d
    print expected
    assert_equal(str(d), expected)

def test_diff_list_2nd_longer():
    a = [3]
    b = [4, 5]
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        @@ @@
        [
        -3,
        +4,
        +5,
        ]''')
    print d
    print expected
    assert_equal(str(d), expected)

def test_diff_list_list():
    a = [1, [2, 3], 4]
    b = [1, 4]
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        @@ @@
        [
         1,
        -[2, 3],
         4,
        ]''')
    assert_equal(str(d), expected)

def test_diff_list_dict():
    a = [1, {'a': 'b'}, 4]
    b = [1, 4]
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        @@ @@
        [
         1,
        -{'a': 'b'},
         4,
        ]''')
    assert_equal(str(d), expected)

def test_diff_list_set():
    a = [1, set([8, 9]), 4]
    b = [1, 4]
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        @@ @@
        [
         1,
        -set([8, 9]),
         4,
        ]''')
    assert_equal(str(d), expected)

def test_diff_seq_objects():
    class FooSeq(object):
        def __init__(self, list):
            self.list = list
        def __len__(self):
            return len(self.list)
        def __iter__(self):
            return iter(self.list)
        def __getitem__(self, x):
            return self.list[x]
    
    d = diff(FooSeq([1]), FooSeq([1,2]))
    expected = dedent('''\
        --- a
        +++ b
        @@ @@
        FooSeq([
         1,
        +2,
        ])''')
    print d
    print expected
    assert_equal(str(d), expected)

def test_tuple():
    d = diff((1,2), (1,3))
    expected = dedent('''\
        --- a
        +++ b
        @@ @@
        (
         1,
        -2,
        +3,
        )''')
    assert_equal(str(d), expected)

def test_diff_dict():
    a = dict(zero=0, one=1, two=2, three=3)
    b = dict(zero='@', one=1, three=3, four=4)
    d = diff(a, b)
    print d
    expected = dedent('''\
        --- a
        +++ b
        @@ @@
        {
        +'four': 4,
        -'zero': 0,
        +'zero': '@',
         'three': 3,
         'one': 1,
        -'two': 2,
        }''')
    print expected
    assert_equal(str(d), expected)

def test_diff_dict_complex():
    a = dict(a=1, b=dict(foo='bar'))
    b = dict(a=1)
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        @@ @@
        {
         'a': 1,
        -'b': {'foo': 'bar'},
        }''')
    print d
    print expected
    assert_equal(str(d), expected)

def test_diff_set(set_type=set):
    a = set_type([1, 3, 5, 7, 'abc', 'def'])
    b = set_type(['qwert', 3, 7, 'abc'])
    d = diff(a, b)
    print d
    expected = dedent('''\
        --- a
        +++ b
        @@ @@
        %s([
         3,
         'abc',
         7,
        -1,
        -5,
        -'def',
        +'qwert',
        ])''') % set_type.__name__
    print expected
    assert_equal(str(d), expected)
    
def test_diff_frozenset():
    return test_diff_set(set_type=frozenset)

def test_eval_bool():
    d = diff([1], [1])
    assert_equal(bool(d), False)
    
    d = diff([1], [2])
    assert_equal(bool(d), True)
    
    d = diff(dict(a=1), dict(a=1))
    assert_equal(bool(d), False)

def test_equal():
    d = diff([1], [1])
    assert_equal(str(d), '')
