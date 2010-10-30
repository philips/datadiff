from textwrap import dedent
from datetime import datetime

import nose
from nose.tools import assert_equal, raises, assert_false, assert_true, assert_raises

from datadiff import diff, DataDiff, NotHashable

if __name__ == '__main__': nose.main()

def test_diff_objects():
    class Foo(object): pass
    try:
        diff(Foo(), Foo())
    except Exception as e:
        assert_equal(type(e), TypeError, "Raised exception should be TypeError")
    else:
        assert "Should've raised a TypeError"

def test_diff_list():
    a = [1,'x', 2, 3, 4, 5]
    b = [1,'y', 2, 4, 6]
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        [
        @@ -0,5 +0,4 @@
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

def test_diff_list_context():
    a = [1]*50 + [2, 3, 4, 5] + [1]*10
    b = [1]*50 + [3, 7] + [1]*10
    d = diff(a, b)
    expected = dedent('''\
        --- a
        +++ b
        [
        @@ -46,56 +46,54 @@
         1,
         1,
         1,
        -2,
         3,
        -4,
        -5,
        +7,
         1,
         1,
         1,
        @@  @@
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
        [
        @@ -0 +0,1 @@
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
        FooSeq([
        @@ -0 +0,1 @@
         1,
        +2,
        ])''')
    print d
    print expected
    assert_equal(str(d), expected)

def test_diff_almost_seq_objects():
    class FooSeq(object):
        def __init__(self, list):
            self.list = list
        def __iter__(self):
            return iter(self.list)
    
    assert_raises(TypeError, diff, FooSeq([1]), FooSeq([1,2]))
  
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
    print d
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
    print expected
    assert_equal(str(d), expected)

def test_diff_dict_keytypes():
    a = {}
    b = {datetime(2010,10,28): 1, True: 1, 2: 2}
    d = diff(a, b)
    print d
    expected = dedent('''\
        --- a
        +++ b
        {
        +True: 1,
        +2: 2,
        +datetime.datetime(2010, 10, 28, 0, 0): 1,
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
        %s([
        -1,
        -5,
        -'def',
        +'qwert',
         3,
         'abc',
         7,
        ])''') % set_type.__name__
    print expected
    assert_equal(str(d), expected)

def test_diff_set_context():
    a = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
    b = set([1, 2, 3, 4, 5, 6, 7, 8])
    d = diff(a, b)
    print d
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

@raises(TypeError)
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