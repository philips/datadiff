from textwrap import dedent

from nose.tools import assert_equal, raises

from datadiff import diff

from pprint import pformat

@raises(Exception)
def test_diff_objects():
    class Foo(object): pass
    diff(Foo(), Foo())

def test_diff_list():
    a = [1,'x', 2, 3, 4, 5]
    b = [1,'y', 2, 4, 6]
    d = diff(a, b)
    expected = dedent('''\
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
        [
        -3,
        +4,
        +5,
        ]''')
    print d
    print expected
    assert_equal(str(d), expected)

# PHP:
"""
--- Expected
+++ Actual
@@ @@
 Array
 (
     [0] => HTTP/1.1 301 Moved Permanently
-    [1] => Location: http://sf-dbrondsema-5010.sb.sf.net/projects/project1/files/proj1.file1.tgz/download?use_mirror=master
+    [1] => Location: http://sf-dbrondsema-5010.sb.sf.net/projects/project1/files
 )
"""
 
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

def test_diff_set(set_type=set):
    a = set_type([1, 3, 5, 7, 'abc', 'def'])
    b = set_type(['qwert', 3, 7, 'abc'])
    d = diff(a, b)
    print d
    expected = dedent('''\
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
