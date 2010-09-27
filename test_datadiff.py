from textwrap import dedent

from nose.tools import assert_equal

from datadiff import diff

def test_diff_list():
    a = [1,'x', 2, 3, 4]
    b = [1,'y', 2, 4, 5]
    d = diff(a, b)
    expected = dedent('''\
        [
         1,
        -'x',
        +'y',
         2,
        -3,
         4,
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
