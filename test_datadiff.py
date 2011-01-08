from textwrap import dedent
from datetime import datetime
import sys
import re

from nose.tools import assert_raises, assert_equal, raises

from datadiff import diff, DataDiff, NotHashable, DiffNotImplementedForType, DiffTypeError

# support 3.0/2.7 set literals, and <2.7
set_start, set_end = repr(set([0])).split('0')
frozenset_start, frozenset_end = repr(frozenset([0])).split('0')

def test_diff_objects():
    class Foo(object): pass
    try:
        diff(Foo(), Foo())
    except Exception:
        e = sys.exc_info()[1]
        assert_equal(type(e), DiffNotImplementedForType,
                     "Raised exception should be DiffNotImplementedForType")
        assert_equal(e.attempted_type, Foo)
    else:
        raise AssertionError("Should've raised a DiffNotImplementedForType")

def test_diff_oneline_strings():
    try:
        diff('foobar', 'baz')
    except Exception:
        e = sys.exc_info()[1]
        assert_equal(type(e), DiffNotImplementedForType,
                     "Raised exception should be DiffNotImplementedForType")
        assert_equal(e.attempted_type, str)
    else:
        raise AssertionError("Should've raised a DiffNotImplementedForType")

def test_diff_multiline_strings():
    d = diff('abc\ndef\nghi', 'abc\nghi')
    expected = dedent('''\
        --- a 
        +++ b 
        @@ -1,3 +1,2 @@
         abc
        -def
         ghi''')
    assert_equal(str(d), expected)

def test_diff_list():
    a = [1,'xyz', 2, 3, 4, 5]
    b = [1,'abc', 2, 4, 6]
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        [
        @@ -0,5 +0,4 @@
         1,
        -'xyz',
        +'abc',
         2,
        -3,
         4,
        -5,
        +6,
        ]''')
    assert_equal(str(d), expected)

def test_diff_list_context():
    a = [1]*50 + [2, 3, 4, 5, 6, 7, 8] + [1]*10
    b = [1]*50 + [3, 9, 10] + [1]*10
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        [
        @@ -46,59 +46,55 @@
         1,
         1,
         1,
        -2,
         3,
        -4,
        -5,
        -6,
        -7,
        -8,
        +9,
        +10,
         1,
         1,
         1,
        @@  @@
        ]''')
    assert_equal(str(d), expected)

def test_diff_list_2nd_longer():
    a = [3]
    b = [4, 5]
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        [
        @@ -0 +0,1 @@
        -3,
        +4,
        +5,
        ]''')
    assert_equal(str(d), expected)

def test_diff_list_list():
    a = [1, [2, 3], 4]
    b = [1, 4]
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        [
        @@ -0,2 +0,1 @@
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
        [
        @@ -0,2 +0,1 @@
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
        [
        @@ -0,2 +0,1 @@
         1,
        -%s8, 9%s,
         4,
        ]''') % (set_start, set_end)
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
        FooSeq([
        @@ -0 +0,1 @@
         1,
        +2,
        ])''')
    assert_equal(str(d), expected)

def test_diff_almost_seq_objects():
    class FooSeq(object):
        def __init__(self, list):
            self.list = list
        def __iter__(self):
            return iter(self.list)
    
    assert_raises(DiffTypeError, diff, FooSeq([1]), FooSeq([1,2]))
  
def test_tuple():
    d = diff((1,2), (1,3))
    expected = dedent('''\
        --- a
        +++ b
        (
        @@ -0,1 +0,1 @@
         1,
        -2,
        +3,
        )''')
    assert_equal(str(d), expected)

def test_diff_dict():
    a = dict(zero=0,   one=1, two=2, three=3,         nine=9, ten=10)
    b = dict(zero='@', one=1,        three=3, four=4, nine=9, ten=10)
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        {
        +'four': 4,
         'nine': 9,
         'ten': 10,
         'three': 3,
        -'two': 2,
        -'zero': 0,
        +'zero': '@',
        @@  @@
        }''')
    assert_equal(str(d), expected)

def test_diff_dict_keytypes():
    a = {}
    b = {datetime(2010,10,28): 1, True: 1, 2: 2}
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        {
        +True: 1,
        +2: 2,
        +datetime.datetime(2010, 10, 28, 0, 0): 1,
        }''')
    assert_equal(str(d), expected)

def test_diff_dict_complex():
    a = dict(a=1, b=dict(foo='bar'))
    b = dict(a=1)
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        {
         'a': 1,
        -'b': {'foo': 'bar'},
        }''')
    assert_equal(str(d), expected)

def test_diff_set(set_type=set):
    a = set_type([1, 3, 5, 7, 'abc', 'def'])
    b = set_type(['qwert', 3, 7, 'abc'])
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        %s([
        -1,
        -5,
        -'def',
        +'qwert',
         3,
         'abc',
         7,
        ])''') % set_type.__name__
    assert_equal(str(d), expected)

def test_diff_set_context():
    a = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
    b = set([1, 2, 3, 4, 5, 6, 7, 8])
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        set([
        -9,
         1,
         2,
         3,
        @@  @@
        ])''')
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

@raises(DiffTypeError)
def test_diff_types():
    d = diff([1], {1:1})

@raises(Exception)
def test_DataDiff_init_params():
    DataDiff(list, '[')
    
def test_DataDiff_change_type():
    dd = DataDiff(list, '[', ']')
    dd.multi('foobar', [1234])
    assert_raises(Exception, str, dd)
    
def test_unhashable_type():
    a = []
    b = [slice(1)]
    assert_raises(NotHashable, diff, a, b)

def test_recursive_list():
    a = [1, [7, 8, 9, 10, 11], 3]
    b = [1, [7, 8,    10, 11], 3]
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        [
        @@ -0,2 +0,2 @@
         1,
         [
         @@ -0,4 +0,3 @@
          7,
          8,
         -9,
          10,
          11,
         ],
         3,
        ]''')
    assert_equal(str(d), expected)
    
def test_recursive_tuple_different_types():
    a = (1, (7, 8,  9, 10, 11), 3)
    b = (1, (7, 8, 'a', 10, 11), 3)
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        (
        @@ -0,2 +0,2 @@
         1,
         (
         @@ -0,4 +0,4 @@
          7,
          8,
         -9,
         +'a',
          10,
          11,
         ),
         3,
        )''')
    assert_equal(str(d), expected)
    
def test_recursive_dict():
    a = dict(a=1, b=dict(foo=17, bar=19), c=3)
    b = dict(a=1, b=dict(foo=17,       ), c=3)
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        {
         'a': 1,
         'b': {
         -'bar': 19,
          'foo': 17,
         },
         'c': 3,
        }''')
    assert_equal(str(d), expected)
    
def test_recursive_set():
    a = set([1, 2, frozenset([3, 4, 5]), 8])
    b = set([1, 2, frozenset([3, 2, 5]), 8])
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        set([
        -%s3, 4, 5%s,
        +%s2, 3, 5%s,
         8,
         1,
         2,
        ])''' % (frozenset_start, frozenset_end,
                 frozenset_start, frozenset_end))
    assert_equal(str(d), expected)
