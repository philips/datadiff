import logging
from difflib import SequenceMatcher

log = logging.getLogger('datadiff')

def diff(a, b):
    try:
        return diff_seq(a, b)
    except:
        if type(a) == type(b) == dict:
            return diff_dict(a, b)
        else:
            log.exception('tried SequenceMatcher but got error')
            raise Exception("not implemented for this type")

class DataDiff(object):
    
    def __init__(self, datatype):
        self.datatype = datatype
        self.diffs = []
    
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
        output = []
        if self.datatype == list:
            output.append('[')
        elif self.datatype == dict:
            output.append('{')
        else:
            raise Exception(self.datatype)
        for change, items in self.diffs:
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
        if self.datatype == list:
            output.append(']')
        elif self.datatype == dict:
            output.append('}')
        else:
            raise Exception(self.datatype)
        return '\n'.join(output)

def diff_seq(a, b):
    sm = SequenceMatcher(a=a, b=b)
    diff = DataDiff(list)
    for chunk in sm.get_grouped_opcodes():
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
    return diff


class dictitem(tuple):
    def __repr__(self):
        return "'%s': %r" % (self[0], self[1]) 

def diff_dict(a, b, context=4):
    diff = DataDiff(dict)
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