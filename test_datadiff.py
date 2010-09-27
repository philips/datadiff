from textwrap import dedent

from nose.tools import assert_equal

from datadiff import diff

def test_diff_list():
    a = [1,2,3]
    b = [1,2]
    d = diff(a, b)
    expected = dedent('''\
        [
         1,
         2,
        -3,
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
    a = dict(one=1, two=2)
    b = dict(one=1, three=3)
    d = diff(a, b)
    print d
    assert_equal(str(d), None)
