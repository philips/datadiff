"""
Copyright 2010 Dave Brondsema

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from difflib import SequenceMatcher, unified_diff
import sys
import os
try:
    from numbers import Number
except ImportError:
    import types
    Number = (complex, int, long, float)


log = logging.getLogger('datadiff')


def parse_version_from_setup():
    _setup = open(os.path.join(os.path.dirname(__file__), '../setup.py'))
    for line in _setup:
        if 'version' in line:
            version = line.split('=')[1].strip(", '\n")
            break
    _setup.close()
    return version
try:
    import pkg_resources
    __version__ = pkg_resources.require("datadiff")[0].version
except:
    try:
        __version__ = parse_version_from_setup
    except:
        __version__ = None



"""
For each type, we need:
* a diff()
* start/end strings
* conversion to hashable
"""

class NotHashable(TypeError): pass
class NotSequence(TypeError): pass
class DiffNotImplementedForType(TypeError):
    def __init__(self, attempted_type):
        self.attempted_type = attempted_type
    def __str__(self):
        return "diff() not implemented for %s" % self.attempted_type

def unified_diff_strings(a, b, fromfile='', tofile='', fromfiledate='', tofiledate='', n=3):
    """
    Wrapper around difflib.unified_diff that accepts 'a' and 'b' as multi-line strings
    and returns a multi-line string, instead of lists of strings.
    """
    return '\n'.join(unified_diff(a.split('\n'), b.split('\n'),
                                  fromfile, tofile, fromfiledate, tofiledate, n,
                                  lineterm=''))

def diff(a, b):
    if type(a) != type(b):
        raise TypeError('Types differ: a=%s b=%s Values of a and b are: %r, %r' % (type(a), type(b), a, b))
    if type(a) == str:
        # special cases
        if '\n' in a or '\n' in b:
            return unified_diff_strings(a, b, fromfile='a', tofile='b')
        else:
            # even though technically it is a sequence,
            # we don't want to diff char-by-char
            raise DiffNotImplementedForType(str)
    if type(a) == dict:
        return diff_dict(a, b)
    if hasattr(a, 'intersection') and hasattr(a, 'difference'):
        return diff_set(a, b)
    try:
        return try_diff_seq(a, b)
    except NotSequence:
        raise DiffNotImplementedForType(type(a))

class DataDiff(object):
    
    def __init__(self, datatype, type_start_str=None, type_end_str=None):
        self.diffs = []
        self.datatype = datatype
        if type_end_str is None:
            if type_start_str is not None:
                raise Exception("Must specify both type_start_str and type_end_str, or neither")
            self.type_start_str = datatype.__name__ + '(['
            self.type_end_str = '])'
        else:
            self.type_start_str = type_start_str
            self.type_end_str = type_end_str

    def context(self, a_start, a_end, b_start, b_end):
        self.diffs.append(('context', [a_start, a_end, b_start, b_end]))

    def context_end_container(self):
        self.diffs.append(('context_end_container', []))
        
    def nested(self, datadiff):
        self.diffs.append(('datadiff', datadiff))

    def multi(self, change, items):
        self.diffs.append((change, items))
        
    def delete(self, item):
        return self.multi('delete', [item])
    
    def insert(self, item):
        return self.multi('insert', [item])
    
    def equal(self, item):
        return self.multi('equal', [item])
        
    def insert_multi(self, items):
        return self.multi('insert', items)
    
    def delete_multi(self, items):
        return self.multi('delete', items)
    
    def equal_multi(self, items):
        return self.multi('equal', items)
    
    def __str__(self):
        return self.stringify()
        
    def stringify(self, depth=0):
        if not self.diffs:
            return ''
        output = []
        if depth == 0:
            output.append('--- a')
            output.append('+++ b')
        output.append(' '*depth + self.type_start_str)
        for change, items in self.diffs:
            if change == 'context':
                context_a = str(items[0])
                if items[0] != items[1]:
                    context_a += ',' + str(items[1])
                context_b = str(items[2])
                if items[2] != items[3]:
                    context_b += ',' + str(items[3])
                output.append(' '*depth + '@@ -%s +%s @@' % (context_a, context_b))
                continue
            if change == 'context_end_container':
                output.append(' '*depth + '@@  @@')
                continue
            elif change == 'datadiff':
                output.append(' '*depth + items.stringify(depth+1) + ',')
                continue
            if change == 'delete':
                ch = '-'
            elif change == 'insert':
                ch = '+'
            elif change == 'equal':
                ch = ' '
            else:
                raise Exception('Unknown change type %r' % change)
            for item in items:
                output.append(' '*depth + "%s%r," % (ch, item))
        output.append(' '*depth + self.type_end_str)
        return '\n'.join(output)
    
    def __nonzero__(self):
        return self.__bool__()
    
    def __bool__(self):
        return bool([d for d in self.diffs if d[0] != 'equal'])

def hashable(s):
    if type(s) == list:
        return tuple(s)
    elif type(s) == dict:
        return frozenset(s.items())
    elif type(s) == set:
        return frozenset(s)
    else:
        try:
            hash(s)
        except TypeError:
            raise NotHashable("Not a hashable type (and it needs to be, for its parent diff): %s" % s)
        return s

def try_diff_seq(a, b, context=3):
    """
    Safe to try any containers with this function, to see if it might be a sequence
    Raises TypeError if its not a sequence
    """
    try:
        return diff_seq(a, b, context)
    except NotHashable:
        raise
    except:
        log.debug('tried SequenceMatcher but got error', exc_info=True)
        raise NotSequence("Cannot use SequenceMatcher on %s" % type(a))

def diff_seq(a, b, context=3):
    if not hasattr(a, '__iter__') and not hasattr(a, '__getitem__'):
        raise NotSequence("Not a sequence %s" % type(a))
    hashable_a = [hashable(_) for _ in a]
    hashable_b = [hashable(_) for _ in b]
    sm = SequenceMatcher(a = hashable_a, b = hashable_b)
    if type(a) == tuple:
        ddiff = DataDiff(tuple, '(', ')')
    elif type(b) == list:
        ddiff = DataDiff(list, '[', ']')
    else:
        ddiff = DataDiff(type(a))
    for chunk in sm.get_grouped_opcodes(context):
        ddiff.context(max(chunk[0][1]-1,0), max(chunk[-1][2]-1, 0),
                     max(chunk[0][3]-1,0), max(chunk[-1][4]-1, 0))
        for change, i1, i2, j1, j2 in chunk:
            if change == 'replace':
                consecutive_deletes = []
                consecutive_inserts = []
                for a2, b2 in zip(a[i1:i2], b[j1:j2]):
                    try:
                        nested_diff = diff(a2, b2)
                        ddiff.delete_multi(consecutive_deletes)
                        ddiff.insert_multi(consecutive_inserts)
                        consecutive_deletes = []
                        consecutive_inserts = []
                        ddiff.nested(nested_diff)
                    except DiffNotImplementedForType:
                        consecutive_deletes.append(a2)
                        consecutive_inserts.append(b2)
                
                # differing lengths get truncated by zip()
                # here we handle the truncated items
                ddiff.delete_multi(consecutive_deletes)
                if i2-i1 > j2-j1:
                    common_length = j2-j1 # covered by zip
                    ddiff.delete_multi(a[i1+common_length:i2])
                ddiff.insert_multi(consecutive_inserts)
                if i2-i1 < j2-j1:
                    common_length = i2-i1 # covered by zip
                    ddiff.insert_multi(b[j1+common_length:j2])
            else:
                if change == 'insert':
                    items = b[j1:j2]
                else:
                    items = a[i1:i2]
                ddiff.multi(change, items)
        if i2 < len(a):
            ddiff.context_end_container()
    return ddiff


class dictitem(tuple):
    def __repr__(self):
        return "%r: %r" % (self[0], self[1])

def diff_dict(a, b, context=3):
    diff = DataDiff(dict, '{', '}')
    for key in a.keys():
        if key not in b:
            diff.delete(dictitem((key, a[key])))
        elif a[key] != b[key]:
            diff.delete(dictitem((key, a[key])))
            diff.insert(dictitem((key, b[key])))
        else:
            if context:
                diff.equal(dictitem((key, a[key])))
            context -= 1
    for key in b:
        if key not in a:
            diff.insert(dictitem((key, b[key])))

    def diffitem_dictitem_sort_key(diffitem):
        change, dictitem = diffitem
        key = dictitem[0][0]
        # use hash, to make sure its always orderable against other potential key types
        basestring = basestring if sys.version[0] == 2 else str
        if isinstance(key, basestring) or isinstance(key, Number):
            return key
        else:
            return abs(hash(key)) # abs for consistency between py2/3, at least for datetime
    diff.diffs.sort(key=diffitem_dictitem_sort_key)

    if context < 0:
        diff.context_end_container()

    return diff

def diff_set(a, b, context=3):
    diff = DataDiff(type(a))
    diff.delete_multi(a - b)
    diff.insert_multi(b - a)
    equal = list(a.intersection(b))
    diff.equal_multi(equal[:context])
    if len(equal) > context:
        diff.context_end_container()
    return diff
