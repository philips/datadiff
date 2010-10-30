import logging
from difflib import SequenceMatcher

log = logging.getLogger('datadiff')


"""
For each type, we need:
* a diff()
* start/end strings
* conversion to hashable
"""

class NotHashable(TypeError): pass
class NotSequence(TypeError): pass

def diff(a, b):
    if type(a) != type(b):
        raise TypeError('Types differ: a=%s b=%s Values of a and b are: %r, %r' % (type(a), type(b), a, b))
    if type(a) == dict:
        return diff_dict(a, b)
    if hasattr(a, 'intersection') and hasattr(a, 'difference'):
        return diff_set(a, b)
    try:
        return try_diff_seq(a, b)
    except NotSequence:
        raise TypeError("diff() not implemented for this type %s" % type(a))

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
                output.append('@@  @@')
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
    if not hasattr(a, '__iter__') or not hasattr(b, '__iter__'):
        raise NotSequence("Not a sequence %s" % type(a))
    hashable_a = [hashable(_) for _ in a]
    hashable_b = [hashable(_) for _ in b]
    sm = SequenceMatcher(a = hashable_a, b = hashable_b)
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

    def diffitem_dictitem_cmp(diffitem1, diffitem2):
        change1, dictitem1 = diffitem1
        change2, dictitem2 = diffitem2
        try:
            return cmp(dictitem1[0], dictitem2[0])
        except TypeError:
            return 1 # whatever
    diff.diffs.sort(cmp=diffitem_dictitem_cmp)

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
