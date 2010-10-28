import logging
from difflib import SequenceMatcher

log = logging.getLogger('datadiff')


"""
For each type, we need:
* a diff()
* start/end strings
* conversion to hashable
"""

def diff(a, b):
    if type(a) != type(b):
        return 'Types differ: %s %s' % (type(a), type(b)) # TODO preview of values
    if type(a) == dict:
        return diff_dict(a, b)
    if hasattr(a, 'intersection') and hasattr(a, 'difference'):
        return diff_set(a, b)
    try:
        return diff_seq(a, b)
    except:
        log.exception('tried SequenceMatcher but got error')
        raise Exception("not implemented for this type")

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
        if not self.diffs:
            return ''
        output = [
            '--- a',
            '+++ b',
        ]
        output.append(self.type_start_str)
        for change, items in self.diffs:
            if change == 'context':
                context_a = str(items[0])
                if items[0] != items[1]:
                    context_a += ',' + str(items[1])
                context_b = str(items[2])
                if items[2] != items[3]:
                    context_b += ',' + str(items[3])
                output.append('@@ -%s +%s @@' % (context_a, context_b))
                continue
            if change == 'context_end_container':
                output.append('@@ @@')
                continue
            if change == 'delete':
                ch = '-'
            elif change == 'insert':
                ch = '+'
            elif change == 'equal':
                ch = ' '
            else:
                raise Exception(items)
            for item in items:
                output.append("%s%r," % (ch, item))
        output.append(self.type_end_str)
        return '\n'.join(output)
    
    def __nonzero__(self):
        return self.__bool__()
    
    def __bool__(self):
        return bool([d for d in self.diffs if d[0] != 'equal'])

def hashable(s):
    if type(s) == list:
        return tuple(s)
    elif type(s) == dict:
        return frozenset(s.iteritems())
    elif type(s) == set:
        return frozenset(s)
    else:
        try:
            hash(s)
        except TypeError:
            raise Exception("Not a hashable type (and it needs to be, for its parent diff): %s" % s)
        return s

def diff_seq(a, b, context=3):
    sm = SequenceMatcher(a = [hashable(_) for _ in a],
                         b = [hashable(_) for _ in b])
    if type(a) == tuple:
        diff = DataDiff(tuple, '(', ')')
    elif type(b) == list:
        diff = DataDiff(list, '[', ']')
    else:
        diff = DataDiff(type(a))
    for chunk in sm.get_grouped_opcodes(context):
        diff.context(max(chunk[0][1]-1,0), max(chunk[-1][2]-1, 0),
                     max(chunk[0][3]-1,0), max(chunk[-1][4]-1, 0))
        for change, i1, i2, j1, j2 in chunk:
            if change == 'insert':
                items = b[j1:j2]
            else:
                items = a[i1:i2]
            if change == 'replace':
                diff.delete_multi(a[i1:i2])
                diff.insert_multi(b[j1:j2])
            else:
                diff.multi(change, items)
        if i2 < len(a):
            diff.context_end_container()
    return diff


class dictitem(tuple):
    def __repr__(self):
        return "%r: %r" % (self[0], self[1]) 

def diff_dict(a, b, context=3):
    diff = DataDiff(dict, '{', '}')
    for key in b:
        if key not in a:
            diff.insert(dictitem((key, b[key])))
        elif a[key] != b[key]:
            diff.delete(dictitem((key, a[key])))
            diff.insert(dictitem((key, b[key])))
        elif context:
            diff.equal(dictitem((key, a[key])))
            context -= 1
    for key in a:
        if key not in b:
            diff.delete(dictitem((key, a[key])))
    return diff

def diff_set(a, b, context=3):
    diff = DataDiff(type(a))
    diff.equal_multi(list(a.intersection(b))[:context])
    diff.delete_multi(a - b)
    diff.insert_multi(b - a)
    return diff
